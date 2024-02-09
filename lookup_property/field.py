from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Iterator

from django.db import models
from django.db.models import ForeignObjectRel
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql import Query

from lookup_property.expressions import LookupPropertyCol, extend_expression_to_joined_table

if TYPE_CHECKING:
    from django.db.models.fields.related import ForeignObject, ManyToManyField
    from django.db.models.query_utils import PathInfo

    from lookup_property.decorator import lookup_property
    from lookup_property.typing import Expr

__all__ = [
    "LookupPropertyField",
    "L",
]


class LookupPropertyField(models.Field):
    def __init__(self, model: type[models.Model], target_property: lookup_property) -> None:
        self.model = model  # Required by `LookupPropertyCol` to resolve related lookups
        self.target_property = target_property
        if target_property.state.joins:
            self.path_infos = LazyPathInfo(self, joins=target_property.state.joins)

        super().__init__()
        target_property.field = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    @property
    def expression(self) -> Expr:
        return self.target_property.expression

    def get_col(  # type: ignore[override]
        self,
        alias: str,  # noqa: ARG002
        output_field: models.Field | None = None,  # noqa: ARG002
    ) -> LookupPropertyCol:
        return self.cached_col

    @cached_property
    def cached_col(self) -> LookupPropertyCol:  # type: ignore[override]
        return LookupPropertyCol(target_field=self)

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        # Register property on a concrete implementation of an abstract model
        self.target_property.contribute_to_class(cls, name, private_only=private_only)


class L:
    """Designate a lookup property as a filter condition."""

    def __init__(self, **kwargs: Any) -> None:
        if len(kwargs) != 1:  # pragma: no cover
            msg = "Exactly one keyword argument is required."
            raise ValueError(msg)

        self.lookup, self.value = kwargs.popitem()

        # See. `django.db.models.sql.query.Query.build_filter`
        self.conditional = True

    def resolve_expression(self, query: Query, **kwargs: Any) -> Expr:  # noqa: ARG002
        """Resolve lookup expression and build a lookup expression based on it."""
        field, lookup_parts, joined_tables = self.find_lookup_property_field(query)
        expression = field.expression
        for table_name in reversed(joined_tables):
            expression = extend_expression_to_joined_table(expression, table_name)
        expression = expression.resolve_expression(query)
        return query.build_lookup(lookup_parts, expression, self.value)

    def find_lookup_property_field(self, query: Query) -> tuple[LookupPropertyField, list[str], list[str]]:
        """
        Find the lookup property field based on the given keyword argument.
        Separate any lookup parts afte and tables before the field name.

        >>> l = L(example__full_name__contains="foo")
        >>> l.find_lookup_property_field(query)
        (LookupPropertyField(<full_name>), ['contains'], ['example'])
        """
        joined_tables: list[str] = []
        field_name, *lookup_parts = self.lookup.split(LOOKUP_SEP)

        while True:
            field: LookupPropertyField = query.model._meta.get_field(field_name)

            # If the field is not a lookup property, it should be a related field.
            # Keep track of the joined table, switch the query object to the related object,
            # and continue looking for the lookup property field from the next lookup part.
            if not isinstance(field, LookupPropertyField):
                query.join(query.base_table_class(query.model._meta.db_table, None))
                joined_tables.append(field_name)
                query = Query(model=field.related_model)  # type: ignore[union-attr]
                field_name, lookup_parts = lookup_parts[0], lookup_parts[1:]
                continue

            # If the field is a lookup property, and joins have been defined for it,
            # join those tables to the query object before returning the field,
            # but only if the lookup was wound from a related model.
            if joined_tables and isinstance(field.target_property.state.joins, list):
                joins = field.target_property.state.joins
                fields_map = query.model._meta.fields_map
                tables: list[str] = [fields_map.get(join).related_model._meta.db_table for join in joins]
                for table in tables:
                    query.join(query.base_table_class(table, None))

            break

        return field, lookup_parts, joined_tables


class LazyPathInfo:
    """
    Class used to `trick django.db.models.sql.query.Query.names_to_path`
    into thinking that a LookupPropertyField is a related field, like a
    ForeignKey or OneToOneField. Computes a list of PathInfo objects, which
    will the be used by `django.db.models.sql.query.JoinPromoter` to add
    sql joins to the query, e.g., for `queryset.count()`.
    """

    def __init__(self, field: LookupPropertyField, *, joins: list[str] | bool = True) -> None:
        self.field = field
        self.joins: list[str] = joins if isinstance(joins, list) else []

    def __iter__(self) -> Iterator[PathInfo]:
        return iter([self[0]])

    def __getitem__(self, item: int) -> PathInfo:
        return self.get_path_info[item]

    @cached_property
    def get_path_info(self) -> list[PathInfo]:
        joins = self.joins
        if not joins:
            expression = self.field.expression
            while hasattr(expression, "source_expressions"):
                expression = expression.source_expressions[0]

            joins = expression.name.split(LOOKUP_SEP)[:1]

        path_info: list[PathInfo] = []
        for join in joins:
            rel_or_field: ForeignObjectRel | ForeignObject | ManyToManyField
            rel_or_field = self.field.model._meta.get_field(join)  # type: ignore[assignment]

            if isinstance(rel_or_field, ForeignObjectRel):
                path_info.extend(rel_or_field.field.get_reverse_path_info())
            else:
                path_info.extend(rel_or_field.get_path_info())

        return path_info
