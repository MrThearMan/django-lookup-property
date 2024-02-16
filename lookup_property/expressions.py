from __future__ import annotations

from contextlib import suppress
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Iterator

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import sql
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import BaseExpression, ResolvedOuterRef
from django.db.models.sql import Query

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models.expressions import Col
    from django.db.models.lookups import Lookup, Transform
    from django.db.models.sql.compiler import SQLCompiler
    from django.db.models.sql.datastructures import Join
    from django.db.models.sql.where import WhereNode

    from .field import LookupPropertyField
    from .typing import Any, Callable, ConvertFunc, Expr


__all__ = [
    "LookupPropertyCol",
    "L",
]


class LookupPropertyCol(models.Expression):
    def __init__(self, target_field: LookupPropertyField) -> None:
        self.target = target_field
        super().__init__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.target!r})"

    @property
    def model(self) -> type[models.Model]:
        return self.target.model

    @property
    def alias(self) -> str:  # pragma: no cover
        return self.target.model._meta.db_table

    @property
    def expression(self) -> Expr:
        return self.target.expression

    @cached_property
    def output_field(self) -> models.Field:
        if hasattr(self.expression, "output_field"):
            return self.expression.output_field
        return self.resolved_target_expression.output_field  # type: ignore[union-attr]

    @cached_property
    def resolved_target_expression(self) -> Col | WhereNode | BaseExpression:
        return self.expression.resolve_expression(sql.Query(self.model))  # type: ignore[return-value]

    def get_lookup(self, name: str) -> type[Lookup] | None:
        return self.target.get_lookup(name)

    def get_transform(self, name: str) -> type[Transform] | None:
        return self.target.get_transform(name)  # pragma: no cover

    def _resolve_joined_lookup(self, query: sql.Query) -> Expr:
        try:
            join: Join = query.alias_map[self.model._meta.db_table]  # type: ignore[assignment]
        except KeyError:
            # Lookup property is referenced with an OuterRef in a Subquery.
            return self.resolved_target_expression  # type: ignore[return-value]

        table_name: str = join.join_field.name  # type: ignore[union-attr,attr-defined]
        return extend_expression_to_joined_table(self.expression, table_name)

    def as_sql(self, compiler: SQLCompiler, connection: BaseDatabaseWrapper) -> tuple[str, list[Any]]:
        expression: Expr = self.expression
        if self.model != compiler.query.model:
            expression = self._resolve_joined_lookup(compiler.query)

        resolved: Col | WhereNode | BaseExpression
        resolved = expression.resolve_expression(compiler.query)  # type: ignore[assignment]

        vendor_impl: Callable[[SQLCompiler, BaseDatabaseWrapper], tuple[str, list[Any]]] | None
        vendor_impl = getattr(resolved, f"as_{connection.vendor}", None)
        if vendor_impl is not None:
            return vendor_impl(compiler, connection)  # type: ignore[no-any-return]

        return resolved.as_sql(compiler, connection)

    @cached_property
    def convert_value(self) -> ConvertFunc:  # pragma: no cover
        if expression_has_output_field(self.expression) and hasattr(self.expression, "convert_value"):
            return self.expression.convert_value
        return super().convert_value


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

        # Check whether the query should be grouped by the lookup expression.
        if expression.contains_aggregate:
            query.group_by = True

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
        from .field import LookupPropertyField

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
                query.join(query.base_table_class(query.model._meta.db_table, query.model._meta.db_table))
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
                    query.join(query.base_table_class(table, table))

            break

        return field, lookup_parts, joined_tables


def expression_has_output_field(expression: Expr) -> bool:  # pragma: no cover
    # Check whether the 'output_field' of the expression can be resolved.
    # This might fail, and does fail for expressions like Trunc if the 'output_field'
    # is not explicitly given (e.g. 'Trunc(F("foo"))' will end up using 'BaseExpression.output_field',
    # which then uses 'BaseExpression.get_source_fields' while F does not have an '_output_field_or_none').
    with suppress(AttributeError):
        return expression.output_field is not None  # type: ignore[union-attr]
    return False


def extend_expression_to_joined_table(expression: Expr, table_name: str) -> Expr:
    """Rewrite the expression so that any containing F and Q expressions are referenced from the given table."""
    if isinstance(expression, models.F):
        expression = deepcopy(expression)
        expression.name = f"{table_name}{LOOKUP_SEP}{expression.name}"
        return expression

    if isinstance(expression, L):
        expression = deepcopy(expression)
        expression.lookup = f"{table_name}{LOOKUP_SEP}{expression.lookup}"
        if hasattr(expression, "value"):
            expression.value = (
                extend_expression_to_joined_table(expression.value, table_name)
                if isinstance(expression.value, (models.F, models.Q, BaseExpression))
                else expression.value
            )
        return expression

    if isinstance(expression, models.Q):
        expression = deepcopy(expression)
        children: list[tuple[str, Any] | models.Q | L] = expression.children  # type: ignore[assignment]
        expression.children = []
        for child in children:
            if isinstance(child, (models.Q, L)):
                expression.children.append(extend_expression_to_joined_table(child, table_name))
            else:
                value = (
                    extend_expression_to_joined_table(child[1], table_name)
                    if isinstance(child[1], (models.F, models.Q, BaseExpression))
                    else child[1]
                )
                expression.children.append((f"{table_name}{LOOKUP_SEP}{child[0]}", value))

        return expression

    # For sub-queries, only OuterRefs are rewritten.
    if isinstance(expression, models.Subquery):
        expression = deepcopy(expression)
        sub_expressions: list[Expr] = expression.query.where.children
        expression.query.where.children = []
        for child in sub_expressions:
            expression.query.where.children.append(extend_subquery_to_joined_table(child, table_name))
        return expression

    expression = deepcopy(expression)
    expressions = [extend_expression_to_joined_table(expr, table_name) for expr in expression.get_source_expressions()]
    expression.set_source_expressions(expressions)
    return expression


def extend_subquery_to_joined_table(expression: Expr, table_name: str) -> Expr:
    if isinstance(expression, (models.OuterRef, ResolvedOuterRef)):
        expression = deepcopy(expression)
        expression.name = f"{table_name}{LOOKUP_SEP}{expression.name}"
        return expression

    expression = deepcopy(expression)
    expressions = [extend_subquery_to_joined_table(expr, table_name) for expr in expression.get_source_expressions()]
    expression.set_source_expressions(expressions)
    return expression
