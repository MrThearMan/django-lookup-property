from __future__ import annotations

import ast
import inspect
from functools import cached_property
from typing import TYPE_CHECKING, overload

from .converters.main import ast_module_to_function, query_expression_ast_module
from .field import LookupPropertyField
from .typing import FunctionType, State

if TYPE_CHECKING:
    from django.db import models

    from .typing import Any, Expr, Self

__all__ = [
    "lookup_property",
]


class lookup_property:  # noqa: N801
    """Decorator for converting a class method to a field"""

    @overload
    def __init__(self, arg: FunctionType) -> None:
        """When using '@lookup_property'."""

    @overload
    def __init__(self, arg: State) -> None:
        """When using '@lookup_property(state=State(...))' to set initial state."""

    def __init__(self, arg: FunctionType | State) -> None:
        # Set in `LookupPropertyField`
        self.field: LookupPropertyField = None  # type: ignore[assignment]

        if not hasattr(self, "state"):
            self.state = arg if isinstance(arg, State) else State()

        if isinstance(arg, FunctionType):
            self.expression: Expr = arg(None)
            self.module = query_expression_ast_module(
                expression=self.expression,
                function_name=arg.__code__.co_name,
                state=self.state,
            )
            self.func = ast_module_to_function(
                module=self.module,
                function_name=arg.__code__.co_name,
                filename=arg.__code__.co_filename,
                state=self.state,
            )

    def __call__(self, func: FunctionType) -> Self:
        self.__init__(func)
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    def __get__(self, instance: models.Model | None, _) -> Any:  # noqa: ANN001
        if instance is None:  # if called on class
            return self
        return self.func(instance)

    def __set__(self, instance: models.Model, value: Any) -> None:
        pass

    def override(self, func: FunctionType) -> None:
        """Override generated function with a custom one."""
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
        cls._meta.add_field(field, private=True)
        setattr(cls, field.attname, self)

    @cached_property
    def func_source(self) -> str:
        """Return the source code generated from the decorated function return expression."""
        return ast.unparse(self.module)
