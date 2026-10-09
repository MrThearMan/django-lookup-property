from __future__ import annotations

import ast
import inspect
import textwrap
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, Unpack, cast, overload

from django.db import models
from django.db.models import sql

from .converters.main import ast_module_to_function, query_expression_ast_module
from .expressions import (
    JoinInfo,
    LookupPropertyCol,
    analyze_joins,
    correlated_subquery,
    extend_expression_to_joined_table,
)
from .typing import LOOKUP_PREFIX, Sentinel, State, StateArgs

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import FunctionType

    from .typing import Expr


__all__ = [
    "LookupPropertyDescriptor",
    "LookupPropertyField",
]


class LookupPropertyDescriptor[R]:
    """Descriptor for accessing a LookupPropertyField on the model."""

    # Set by `override` or `generate_func`
    func: Callable[[Any], R]
    module: ast.Module

    def __init__(self, func: FunctionType, /, **kwargs: Unpack[StateArgs]) -> None:
        # Set in `LookupPropertyField`
        self.field: LookupPropertyField = None  # type: ignore[assignment]

        self.state = State(**kwargs)

        self.__name__ = func.__name__
        self._expression: Callable[[], Expr] = func
        self._code = func.__code__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    @overload
    def __get__(self, instance: None, model: type[models.Model] | None) -> Self: ...

    @overload
    def __get__(self, instance: models.Model, model: type[models.Model] | None) -> R: ...

    def __get__(self, instance: models.Model | None, model: type[models.Model] | None) -> Self | R:
        if instance is None:  # if called on class
            return self
        cached_value = getattr(instance, self.field.attname, Sentinel)
        if cached_value is not Sentinel:
            return cast("R", cached_value)
        return self.func(instance)

    def __set__(self, instance: models.Model, value: Any) -> None:
        # Cache values from queryset annotations to avoid re-evaluating the property on instances.
        # This does allow overriding the value manually, but that is not recommended.
        setattr(instance, self.field.attname, value)

    def override(self, func: Callable[[Any], R]) -> None:
        """Override generated function with a custom one."""
        self.func = func
        self.module = ast.parse(textwrap.dedent(inspect.getsource(func)))

    def generate_func(self) -> None:
        """Generate the python function from the decorated function return expression."""
        self.module = query_expression_ast_module(
            expression=self.expression,
            function_name=self._code.co_name,
            state=self.state,
        )
        self.func = ast_module_to_function(
            module=self.module,
            function_name=self._code.co_name,
            filename=self._code.co_filename,
            state=self.state,
        )

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        # Overrides are set in the class body, which runs before this is called.
        if not hasattr(self, "func"):
            self.generate_func()

        # Called by `django.db.models.base.ModelBase.add_to_class`
        field = LookupPropertyField(cls, target_property=self)
        field.set_attributes_from_name(name)
        field.name = field.attname = f"{LOOKUP_PREFIX}{name}"  # Enable using aliases with the same name as the field
        field.concrete = self.state.concrete  # if False -> Don't include field in `SELECT` statements
        field.hidden = self.state.hidden  # If True -> Don't include field in `model._meta.get_fields()`
        field.generated = True  # type: ignore[misc]  # Don't validate field when `model.clean_fields()` is called
        cls._meta.add_field(field, private=True)
        setattr(cls, name, self)

    @cached_property
    def func_source(self) -> str:
        """Return the source code generated from the decorated function return expression."""
        return ast.unparse(self.module)

    @cached_property
    def expression(self) -> Expr:
        return self._expression()


class LookupPropertyField(models.Field):
    def __init__(self, model: type[models.Model], target_property: LookupPropertyDescriptor) -> None:
        self.model = model  # Required by `LookupPropertyCol` to resolve related lookups
        self.target_property = target_property
        self.join_infos: dict[tuple[type[models.Model], tuple[str, ...]], JoinInfo] = {}

        super().__init__()
        target_property.field = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    @property
    def expression(self) -> Expr:
        return self.target_property.expression

    def get_col(  # type: ignore[override]
        self,
        alias: str | None,
        output_field: models.Field | None = None,
    ) -> LookupPropertyCol:
        return LookupPropertyCol(target_field=self, alias=alias)

    @cached_property
    def cached_col(self) -> LookupPropertyCol:  # type: ignore[override]
        return self.get_col(self.model._meta.db_table)

    def join_info(self, model: type[models.Model] | None = None, joined_tables: tuple[str, ...] = ()) -> JoinInfo:
        """
        Find out which joins the expression needs when it is referenced from the given model
        through the given relations. Defaults to the model the lookup property is defined on.
        """
        key = (model or self.model, joined_tables)
        info = self.join_infos.get(key)
        if info is None:
            expression = self.expression
            for table_name in reversed(joined_tables):
                expression = extend_expression_to_joined_table(expression, table_name)
            info = self.join_infos[key] = analyze_joins(key[0], expression)
        return info

    def resolve_for_alias(self, alias: str | None, outer_query: sql.Query) -> Expr:
        """
        Resolve the expression for the row of the given table alias in the outer query.

        The outer query is already being compiled at this point, so joins can no longer be added to it.
        Expressions that need joins or aggregation are evaluated in a correlated subquery instead.
        """
        info = self.join_info()
        expression = self.expression
        if info.joins or info.aggregate:
            expression = correlated_subquery(self.model, expression)

        query = sql.Query(self.model, alias_cols=alias is not None)
        # Use the same alias naming as the outer query so that subquery aliases don't clash with it.
        query.alias_prefix = outer_query.alias_prefix
        query.subq_aliases = outer_query.subq_aliases
        if alias is not None:
            query.alias_map[alias] = query.base_table_class(self.model._meta.db_table, alias)
            query.alias_refcount[alias] = 1
            query.table_map[self.model._meta.db_table] = [alias]

        return expression.resolve_expression(query, allow_joins=True)  # type: ignore[union-attr,return-value]

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        # Register property on a concrete implementation of an abstract model
        self.target_property.contribute_to_class(cls, name, private_only=private_only)
