from __future__ import annotations

import ast
import inspect
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, Unpack

from django.db import models
from django.db.models import ForeignObjectRel

from .converters.main import ast_module_to_function, query_expression_ast_module
from .expressions import LookupPropertyCol
from .typing import LOOKUP_PREFIX, R, Sentinel, State, StateArgs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import FunctionType

    from django.db.models.fields.related import ForeignObject, ManyToManyField
    from django.db.models.query_utils import PathInfo

    from .typing import Expr


__all__ = [
    "LookupPropertyDescriptor",
    "LookupPropertyField",
]


class LookupPropertyDescriptor(Generic[R]):
    """Descriptor for accessing a LookupPropertyField on the model."""

    def __init__(self, func: FunctionType, /, **kwargs: Unpack[StateArgs]) -> None:
        # Set in `LookupPropertyField`
        self.field: LookupPropertyField = None  # type: ignore[assignment]

        self.state = State(**kwargs)

        self.__name__ = func.__name__
        self._expression: Callable[[], Expr] = lambda: func()
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    def __get__(self, instance: models.Model | None, model: type[models.Model] | None) -> R:
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
        private_only: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        if not hasattr(self, "func"):  # pragma: no cover
            msg = f"Must set function for lookup property with '@{self.__name__}.override'."
            raise ValueError(msg)

        # Called by `django.db.models.base.ModelBase.add_to_class`
        field = LookupPropertyField(cls, target_property=self)
        field.set_attributes_from_name(name)
        field.name = field.attname = f"{LOOKUP_PREFIX}{name}"  # Enable using aliases with the same name as the field
        field.concrete = self.state.concrete  # if False -> Don't include field in `SELECT` statements
        field.hidden = self.state.hidden  # If True -> Don't include field in `model._meta.get_fields()`
        field.generated = True  # Don't validate field when `model.clean_fields()` is called
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
        alias: str,
        output_field: models.Field | None = None,
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


class LazyPathInfo:
    """
    Class used to `trick django.db.models.sql.query.Query.names_to_path`
    into thinking that a LookupPropertyField is a related field, like a
    ForeignKey or OneToOneField. Computes a list of PathInfo objects, which
    will the be used by `django.db.models.sql.query.JoinPromoter` to add
    sql joins to the query, e.g., for `queryset.count()`.
    """

    def __init__(self, field: LookupPropertyField, *, joins: list[str]) -> None:
        self.field = field
        self.joins = joins

    def __iter__(self) -> Iterator[PathInfo]:
        return iter([self[0]])

    def __getitem__(self, item: int) -> PathInfo:
        return self.get_path_info[item]

    @cached_property
    def get_path_info(self) -> list[PathInfo]:
        path_info: list[PathInfo] = []
        for join in self.joins:
            rel_or_field: ForeignObjectRel | ForeignObject | ManyToManyField
            rel_or_field = self.field.model._meta.get_field(join)  # type: ignore[assignment]

            if isinstance(rel_or_field, ForeignObjectRel):
                path_info.extend(rel_or_field.field.get_reverse_path_info())
            else:
                path_info.extend(rel_or_field.get_path_info())

        return path_info
