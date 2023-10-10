from __future__ import annotations

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
    from django.db.models.sql.where import WhereNode

    from .decorator import lookup_property
    from .typing import Any, Callable, Expr


__all__ = [
    "ExpressionCol",
]


class ExpressionCol(models.Expression):
    contains_aggregate = False

    def __init__(
        self,
        expression: Expr,
        model: type[models.Model],
        alias: str,
        target: lookup_property,
    ) -> None:
        self.expression = expression
        self.model = model
        self.alias = alias
        self.target = target
        super().__init__()

    @cached_property
    def output_field(self) -> models.Field:
        if hasattr(self.expression, "output_field"):
            return self.expression.output_field
        expression: Col | WhereNode | BaseExpression
        expression = self.expression.resolve_expression(sql.Query(self.model))  # type: ignore[assignment]
        return expression.output_field  # type: ignore[union-attr]

    def get_lookup(self, name: str) -> type[Lookup] | None:
        return self.target.get_lookup(name)

    def get_transform(self, name: str) -> type[Transform] | None:
        return self.target.get_transform(name)

    def _resolve_joined_lookup(self, query: sql.Query) -> Expr:
        try:
            join = query.alias_map[self.model._meta.db_table]
        except KeyError:
            # Lookup property is referenced with an OuterRef in a Subquery.
            return self.expression.resolve_expression(sql.Query(self.model))  # type: ignore[return-value]

        return reverse_expression(self.expression, join.join_field.name)  # type: ignore[union-attr]

    def as_sql(self, compiler: SQLCompiler, connection: BaseDatabaseWrapper) -> tuple[str, list[Any]]:
        expression: Expr = self.expression
        if self.model != compiler.query.model:
            expression = self._resolve_joined_lookup(compiler.query)

        resolved: Col | WhereNode | BaseExpression
        resolved = expression.resolve_expression(compiler.query)  # type: ignore[assignment]

        vendor_impl: Callable[[SQLCompiler, BaseDatabaseWrapper], tuple[str, list[Any]]] | None
        vendor_impl = getattr(resolved, "as_" + connection.vendor, None)
        if vendor_impl is not None:
            return vendor_impl(compiler, connection)  # type: ignore[no-any-return]

        return resolved.as_sql(compiler, connection)


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
