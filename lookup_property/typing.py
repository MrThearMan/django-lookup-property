from __future__ import annotations

import random
import string
from collections.abc import Callable, Collection, Generator, Iterable
from dataclasses import dataclass, field
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Literal,
    ParamSpec,
    Protocol,
    Self,
    TypeAlias,
    TypedDict,
    TypeVar,
    cast,
)

from django.conf import settings
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models.expressions import BaseExpression, Combinable

if TYPE_CHECKING:
    from django.db.models.sql import Query

__all__ = [
    "LOOKUP_PREFIX",
    "Any",
    "Callable",
    "Collection",
    "Concatenate",
    "ConvertFunc",
    "Expr",
    "FunctionType",
    "Generator",
    "Iterable",
    "Literal",
    "ModelMethod",
    "ParamSpec",
    "Protocol",
    "R",
    "Self",
    "State",
    "StateArgs",
    "TModel",
    "TypeVar",
    "cast",
]


R = TypeVar("R")
TModel = TypeVar("TModel", bound=models.Model)
Expr: TypeAlias = BaseExpression | Combinable | models.Q

LOOKUP_PREFIX = "_lookup_property_"


class ExpressionKind(Protocol):
    def resolve_expression(
        self,
        query: Query,
        allow_joins: bool,  # noqa: FBT001
        reuse: set[str] | None,
        summarize: bool,  # noqa: FBT001
        for_save: bool,  # noqa: FBT001
    ) -> ExpressionKind: ...


ModelMethod = Callable[[TModel], Expr] | Callable[[], Expr]
ConvertFunc = Callable[[Any, BaseExpression, BaseDatabaseWrapper], Any]

Sentinel = object()


def random_arg_name() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))  # noqa: S311


class RandomKeyDict(dict[str, Any]):
    """Custom dict for adding items with random keys."""

    def add(self, item: Any) -> str:
        """Add an item to the dict with a random key. Return the key."""
        name = random_arg_name()
        self.__setitem__(name, item)
        return name


@dataclass
class State:
    joins: list[str] = field(default_factory=list)
    use_tz: bool = field(default_factory=lambda: settings.USE_TZ)
    skip_codegen: bool = False
    concrete: bool = False
    hidden: bool = True

    imports: set[str] = field(default_factory=set, init=False)
    extra_kwargs: RandomKeyDict = field(default_factory=RandomKeyDict, init=False)


class StateArgs(TypedDict, total=False):
    joins: list[str]
    skip_codegen: bool
    use_tz: bool
    concrete: bool
    hidden: bool
