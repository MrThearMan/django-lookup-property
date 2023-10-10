from __future__ import annotations

import ast
import inspect
from functools import cached_property
from typing import TYPE_CHECKING

from django.db import models

from .converters.function import ast_module_to_function, query_expression_ast_module
from .expressions import ExpressionCol
from .typing import State

if TYPE_CHECKING:
    from .typing import Any, Expr, FunctionType

__all__ = [
    "lookup_property",
]


class lookup_property(models.Field):  # noqa: N801
    """Decorator for converting a class method to a field"""

    def __init__(self, func: FunctionType) -> None:
        super().__init__()
        state = State()
        self.expression: Expr = func(None)
        self.module = query_expression_ast_module(
            expression=self.expression,
            function_name=func.__code__.co_name,
            state=state,
        )
        self.func = ast_module_to_function(
            module=self.module,
            function_name=func.__code__.co_name,
            filename=func.__code__.co_filename,
            state=state,
        )

    def __get__(self, instance: models.Model | None, _) -> Any:  # noqa: ANN001
        if instance is None:  # if called on class
            return self
        return self.func(instance)

    def __set__(self, instance: models.Model, value: Any) -> None:
        pass
        # if self.func.__name__ in instance.__dict__:
        #     msg = "Lookup properties cannot be set manually"
        #     raise ValueError(msg)

        # instance.__dict__[self.func.__name__] = value

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002, ARG002
    ) -> None:
        # Called by `django.db.models.base.ModelBase.add_to_class`
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_field(self, private=True)
        if self.column:
            setattr(cls, self.attname, self)

    def get_col(  # type: ignore[override]
        self,
        alias: str,  # noqa: ARG002
        output_field: models.Field | None = None,  # noqa: ARG002
    ) -> ExpressionCol:
        return self.cached_col

    @cached_property
    def cached_col(self) -> ExpressionCol:  # type: ignore[override]
        return ExpressionCol(
            expression=self.expression,
            model=self.model,
            alias=self.model._meta.db_table,
            target=self,
        )

    @cached_property
    def func_source(self) -> str:
        """Return the source code generated from the decorated function return expression."""
        return ast.unparse(self.module)

    def override(self, func: FunctionType) -> None:
        """Override generated function with a custom one."""
        self.func = func
        self.module = ast.parse(inspect.cleandoc(inspect.getsource(func)))

    def alias(self, func: FunctionType) -> None:
        pass  # TODO: Add .alias() to queries?
