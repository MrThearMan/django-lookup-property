from __future__ import annotations

import ast
import inspect
from functools import cached_property
from typing import TYPE_CHECKING, overload

from .converters.main import ast_module_to_function, query_expression_ast_module
from .field import LookupPropertyField
from .typing import FunctionType, SelfNotUsable, Sentinel, State

if TYPE_CHECKING:
    from django.db import models

    from .typing import Any, Callable, Expr, Self

__all__ = [
    "lookup_property",
]


class lookup_property:  # noqa: N801
    """Decorator for converting a class method to a LookupPropertyField"""

    @overload
    def __init__(self, func: FunctionType) -> None:
        """When using '@lookup_property'."""

    @overload
    def __init__(self, *, joins: bool | list[str], use_tz: bool, skip_codegen: bool, concrete: bool) -> None:
        """When using '@lookup_property(...)' to set initial state."""

    def __init__(self, func: FunctionType | None = None, /, **kwargs: Any) -> None:
        # Set in `LookupPropertyField`
        self.field: LookupPropertyField = None  # type: ignore[assignment]

        if not hasattr(self, "state"):
            self.state = State(**kwargs)

        if isinstance(func, FunctionType):
            self._expression: Callable[[], Expr] = lambda: func(SelfNotUsable)
            if self.state.skip_codegen:
                return

            self.module = query_expression_ast_module(
                expression=self.expression,
                function_name=func.__code__.co_name,
                state=self.state,
            )
            self.func = ast_module_to_function(
                module=self.module,
                function_name=func.__code__.co_name,
                filename=func.__code__.co_filename,
                state=self.state,
            )

    def __call__(self, func: FunctionType) -> Self:
        self.__init__(func)  # type: ignore[misc]
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    def __get__(self, instance: models.Model | None, model: type[models.Model] | None) -> Any:
        if instance is None:  # if called on class
            return self
        cached_value = getattr(instance, self.field.attname, Sentinel)
        if cached_value is not Sentinel:
            return cached_value
        return self.func(instance)

    def __set__(self, instance: models.Model, value: Any) -> None:
        # Cache values from queryset annotations to avoid re-evaluating the property on instances.
        # This does allow overriding the value manually, but that is not recommended.
        setattr(instance, self.field.attname, value)

    def override(self, func: FunctionType) -> None:
        """Override generated function with a custom one."""
        if not self.state.skip_codegen:  # pragma: no cover
            msg = "Override is only allowed when lookup property was initialized with `skip_codegen=True`"
            raise ValueError(msg)
        self.func = func
        self.module = ast.parse(inspect.cleandoc(inspect.getsource(func)))

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002, ARG002
    ) -> None:
        # Called by `django.db.models.base.ModelBase.add_to_class`
        field = LookupPropertyField(cls, target_property=self)
        field.set_attributes_from_name(name)
        field.name = field.attname = f"_{name}"  # Enable using aliases with the same name as the field
        field.concrete = self.state.concrete  # if False -> Don't include field in `SELECT` statements
        cls._meta.add_field(field, private=True)
        setattr(cls, name, self)

    @cached_property
    def func_source(self) -> str:
        """Return the source code generated from the decorated function return expression."""
        return ast.unparse(self.module)

    @cached_property
    def expression(self) -> Expr:
        return self._expression()
