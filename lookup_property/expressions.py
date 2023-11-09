from __future__ import annotations

from contextlib import suppress
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import sql
from django.db.models.constants import LOOKUP_SEP

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models.expressions import BaseExpression, Col
    from django.db.models.lookups import Lookup, Transform
    from django.db.models.sql.compiler import SQLCompiler
    from django.db.models.sql.datastructures import Join
    from django.db.models.sql.where import WhereNode

    from .field import LookupPropertyField
    from .typing import Any, Callable, ConvertFunc, Expr


__all__ = [
    "LookupPropertyCol",
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
            join: Join = query.alias_map[self.model._meta.db_table]
        except KeyError:
            # Lookup property is referenced with an OuterRef in a Subquery.
            return self.resolved_target_expression  # type: ignore[return-value]

        return reverse_expression(self.expression, join.join_field.name)  # type: ignore[union-attr]

    def as_sql(self, compiler: SQLCompiler, connection: BaseDatabaseWrapper) -> tuple[str, list[Any]]:
        expression: Expr = self.expression
        if self.model != compiler.query.model:
            expression = self._resolve_joined_lookup(compiler.query)

        resolved: Col | WhereNode | BaseExpression
        resolved = expression.resolve_expression(compiler.query)  # type: ignore[assignment]

        vendor_impl: (Callable[[SQLCompiler, BaseDatabaseWrapper], tuple[str, list[Any]]] | None)
        vendor_impl = getattr(resolved, f"as_{connection.vendor}", None)
        if vendor_impl is not None:
            return vendor_impl(compiler, connection)  # type: ignore[no-any-return]

        return resolved.as_sql(compiler, connection)

    @cached_property
    def convert_value(self) -> ConvertFunc:
        if expression_has_output_field(self.expression) and hasattr(self.expression, "convert_value"):
            return self.expression.convert_value
        return super().convert_value


def expression_has_output_field(expression: Expr) -> bool:
    # Check whether the 'output_field' of the expression can be resolved.
    # This might fail, and does fail for expressions like Trunc if the 'output_field'
    # is not explicitly given (e.g. 'Trunc(F("foo"))' will end up using 'BaseExpression.output_field',
    # which then uses 'BaseExpression.get_source_fields' while F does not have an '_output_field_or_none').
    with suppress(AttributeError):
        return expression.output_field is not None
    return False


def reverse_expression(expression: Expr, key: str) -> Expr:
    if isinstance(expression, models.F):
        return models.F(f"{key}{LOOKUP_SEP}{expression.name}")

    if isinstance(expression, models.Q):
        children: list[tuple[str, Any]] = expression.children  # type: ignore[assignment]
        return models.Q(**{f"{key}{LOOKUP_SEP}{rest}": value for rest, value in children})

    expression = deepcopy(expression)
    expressions = [reverse_expression(expr, key) for expr in expression.get_source_expressions()]
    expression.set_source_expressions(expressions)  # type: ignore[arg-type]
    return expression
