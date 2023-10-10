import ast
from dataclasses import dataclass, field
from types import FunctionType
from typing import Any, Callable, Concatenate, Iterable, Literal, ParamSpec, Protocol, Self, TypeVar, cast

from django.conf import settings
from django.db import models
from django.db.models.expressions import BaseExpression

__all__ = [
    "Any",
    "Callable",
    "cast",
    "Concatenate",
    "Expr",
    "FunctionType",
    "Iterable",
    "Literal",
    "ModelMethod",
    "ParamSpec",
    "Protocol",
    "Self",
    "State",
    "TModel",
    "TypeVar",
]

TModel = TypeVar("TModel", bound=models.Model)
Expr = BaseExpression | models.F | models.Q
ModelMethod = Callable[[TModel], Expr]


@dataclass
class State:
    imports: set[str] = field(default_factory=set)
    use_tz: bool = field(default_factory=lambda: settings.USE_TZ)
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


def InstanceAttribute(attrs: list[str]) -> ast.Attribute:  # noqa: N802
    """attrs: ["foo", "bar"] -> self.foo.bar"""
    value: ast.Name | ast.Attribute = ast.Name(id="self", ctx=ast.Load())
    attr = attrs.pop()
    if attrs:
        value = InstanceAttribute(attrs)
    return ast.Attribute(value=value, attr=attr, ctx=ast.Load())
