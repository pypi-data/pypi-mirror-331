import json
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Iterable
from uuid import UUID

from json_multi_merge import merge
from sqlalchemy import Engine, Table, func, union
from sqlalchemy.sql import select

Ancestors = Iterable[tuple[UUID, Callable | None]]


def merge_tree(
    db: Any,
    table: Table,
    id: UUID,
    type: str,
    json_field: str,
    parents: ModuleType,
    slugs: Iterable[str] | None = None,
    filters: tuple | None = None,
    buff_query: Callable | None = None,
    debug: str | None = None,
    callback: Callable | None = None,
) -> dict:
    return TreeMerger(
        db=db,
        table=table,
        json_field=json_field,
        parents=parents,
        filters=filters,
        buff_query=buff_query,
        callback=callback,
        debug=debug,
    ).merge(
        resource_id=id,
        resource_type=type,
        slugs=slugs,
    )


@dataclass
class TreeMerger:
    db: Engine
    table: Table
    json_field: str
    parents: ModuleType
    filters: tuple | None = None
    buff_query: Callable | None = None
    callback: Callable | None = None
    debug: str | None = None

    def merge(
        self,
        resource_id: UUID,
        resource_type: str,
        slugs: Iterable[str] | None = None,
    ) -> dict:
        """Take a resource ID and return the merged json object for that page.

        The merged json object is any json saved for that resource, merged into any resources saved
        for its ancestor resources, all the way up the hierarchy.
        """
        # Get a generator that will yield the IDs of a resource's immediate ancestors
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.slugs = slugs
        parent_getter = getattr(self.parents, resource_type, None)

        # Get a generator that will yield the json objects of all the requested resource's ancestors
        json_objects = self.get_json_objects(resource_id, parent_getter)

        # Merge those json objects and return the result
        return merge(*json_objects)

    def get_json_objects(
        self,
        resource_id: UUID,
        parent_getter: Callable[[UUID], Ancestors] | None,
    ) -> Iterable[dict]:
        """Take a resource ID and return all its ancestors' resources.

         Recurses up the hierarchy using "parent getters" to get the IDs of each resource's
         immediate ancestors, then on the way back down yields any resources defined for those
         resources, starting at the top.
        """
        C = self.table.columns
        query = select(self.table)

        # These filters will be used to get the resource config here, and the slug configs later
        filters: tuple = (C.resource_id == resource_id,)
        if self.filters is not None:
            filters += self.filters

        # Hook for altering query and filters before executing
        if callable(self.buff_query):
            query, filters = self.buff_query(C, query, filters)

        # Get this resource's record
        query = query.where(*filters)
        record = self.get_resource_record(query.where(C.slug.is_(None)).order_by(C.created_at))

        # Recurse up the hierarchy
        if parent_getter is not None and getattr(record, 'inherits', True):
            # If this resource isn't the top of the hierarchy, recurse upwards...
            for parent_id, grandparent_getter in parent_getter(resource_id):
                # ...with the parent's ID and a generator of that resource's immediate ancestors
                yield from self.get_json_objects(parent_id, grandparent_getter)

        # As the recursion unwinds, yield any json objects for each resource: first its own,
        # then those for any slugs under it
        if record:
            yield self.record_json(record)
        if self.slugs:
            for slug_record in self.get_slug_records(query, C):
                yield self.record_json(slug_record)

    def get_resource_record(self, query):
        return self.db.execute(query).first()

    def get_slug_records(self, query, C):
        slug_query = None
        if callable(self.buff_query):
            # If we're buffing the query, then we probably need to union the slug filters
            queries = ()
            for slug in self.slugs:
                queries = queries + (query.filter(C.slug == slug).limit(1),)
            union_aliased = union(*queries).alias()
            order = func.array_position(self.slugs, union_aliased.c.slug)
            slug_query = select(union_aliased).order_by(order)
        else:
            order = func.array_position(self.slugs, C.slug)
            slug_query = query.where(C.slug.in_(self.slugs)).order_by(order)
        return self.db.execute(slug_query)

    def record_json(self, record: Any) -> dict:
        if callable(self.callback):
            self.callback(record)

        json_data = getattr(record, self.json_field)

        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        if self.debug is not None:
            self.add_debug_info(json_data, record)

        return json_data

    def add_debug_info(self, json_data, record):
        new_items = []
        for k, v in json_data.items():
            if isinstance(v, dict):
                self.add_debug_info(v, record)
            else:
                new_items.append(self.debug_info(k, v, record))
        json_data.update(new_items)

    def debug_info(self, k: str, v: Any, record: Any) -> tuple[str, dict | list]:
        if self.debug == 'history':
            return k + '-history', [self.from_dict(record) | {'value': v}]
        if self.debug == 'annotate':
            return k + '-from', self.from_dict(record)
        return k, self.from_dict(record)

    def from_dict(self, record: Any) -> dict:
        return dict(self.from_pairs(record))

    def from_pairs(self, record: Any) -> Iterable[tuple[str, str]]:
        yield 'id', str(record.resource_id)
        yield 'type', record.resource_type,
        yield self.json_field + '_id', str(record.id)
        if record.slug:
            yield 'slug', record.slug
        if record.draft_set:
            yield 'draft_set', record.draft_set
