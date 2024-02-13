from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Iterator

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import ForeignObjectRel
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql import Query

from lookup_property.expressions import LookupPropertyCol, extend_expression_to_joined_table
from lookup_property.typing import Sentinel

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

    def get_default(self) -> Any:
        # Default value that makes sure `lookup_property.__get__`
        # does not consider the field as set right after initialization.
        # Called by `Model.__init__`.
        return Sentinel


class L:
    """
    Designate a lookup property as a filter condition or values selection.

    Examples:

    >>> qs.values(full_name_alias=L("full_name"))

    >>> qs.values_list(L("full_name"), flat=True)

    >>> qs.filter(L(full_name__contains="foo"))

    >>> sq = qs_1.filter(name=OuterRef("full_name")).values("pk")
    >>> qs_2.filter(id__in=L(models.Subquery(sq)))
    """

    def __init__(self, __ref: str | models.Subquery = "", /, **kwargs: Any) -> None:
        if __ref:  # pragma: no cover
            if kwargs:
                msg = "Either one positional or keyword argument can be given."
                raise ValueError(msg)

            self.lookup = __ref

        elif len(kwargs) != 1:  # pragma: no cover
            msg = "Exactly one keyword argument is required."
            raise ValueError(msg)

        else:
            self.lookup, self.value = kwargs.popitem()

        self.conditional = True  # See. `django.db.models.sql.query.Query.build_filter`

    def __str__(self) -> str:
        if hasattr(self, "value"):
            return f"{self.__class__.__name__}({self.lookup}={self.value!r})"
        return f"{self.__class__.__name__}({self.lookup!r})"

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[tuple[str, Any] | str]:
        if hasattr(self, "value"):
            return iter([self.lookup, self.value])
        return iter([self.lookup])

    def __len__(self) -> int:
        return len(list(iter(self)))

    def __getitem__(self, item: int) -> Any:
        return list(self)[item]

    def resolve_expression(  # noqa: PLR0913
        self,
        query: Query,
        allow_joins: bool,  # noqa: FBT001
        reuse: Any = None,
        summarize: bool = False,  # noqa: FBT001, FBT002
        for_save: bool = False,  # noqa: ARG002, FBT001, FBT002
    ) -> Expr:
        """Resolve lookup expression and either return it or build a lookup expression based on it."""
        field, lookup_parts, joined_tables = self.find_lookup_property_field(query)
        lookup_name = field.attname.removeprefix("_")
        expression = field.expression
        for table_name in reversed(joined_tables):
            expression = extend_expression_to_joined_table(expression, table_name)

        query.add_annotation(expression, lookup_name, select=False)
        expression = query.annotations[lookup_name]

        # For sub-queries, save the resolved expression in place of the OuterRef.
        if isinstance(self.lookup, models.Subquery):
            for child in self.lookup.query.where.children:
                if getattr(getattr(child, "rhs", None), "name", None) == lookup_name:
                    child.rhs = expression
            expression = self.lookup

        if not hasattr(self, "value"):
            return expression

        value = query.resolve_lookup_value(self.value, reuse, allow_joins, summarize)
        return query.build_lookup(lookup_parts, expression, value)

    def find_lookup_property_field(self, query: Query) -> tuple[LookupPropertyField, list[str], list[str]]:
        """
        Find the lookup property field based on the given keyword argument.
        Separate any lookup parts afte and tables before the field name.

        >>> l = L(example__full_name__contains="foo")
        >>> l.find_lookup_property_field(query)
        (LookupPropertyField(<full_name>), ['contains'], ['example'])
        """
        joined_tables: list[str] = []
        lookup = self.lookup

        # For sub-queries, get the lookup from the sub-query's OuterRef.
        if isinstance(lookup, models.Subquery):
            lookup = lookup.query.where.children[0].rhs.name  # type: ignore[union-a]

        field_name, *lookup_parts = lookup.split(LOOKUP_SEP)

        while True:
            try:
                field: LookupPropertyField = query.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Lookup fields are prefixed with "_" to enable aliasing with the same name.
                field: LookupPropertyField = query.model._meta.get_field(f"_{field_name}")

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
                tables: list[str] = [
                    query.model._meta.get_field(join).related_model._meta.db_table
                    for join in field.target_property.state.joins
                ]
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
