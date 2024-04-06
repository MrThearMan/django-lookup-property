from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Concatenate,
    Generator,
    Iterable,
    Literal,
    ParamSpec,
    Protocol,
    Self,
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
    "Any",
    "Callable",
    "cast",
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
    "Self",
    "State",
    "TModel",
    "TypeVar",
]


TModel = TypeVar("TModel", bound=models.Model)
Expr = BaseExpression | Combinable | models.Q


class ExpressionKind(Protocol):
    def resolve_expression(  # noqa: PLR0913
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
    return "".join(random.choices(string.ascii_lowercase, k=20))


class RandomKeyDict(dict[str, Any]):
    """Custom dict for adding items with random keys."""

    def add(self, item: Any) -> str:
        """Add an item to the dict with a random key. Return the key."""
        name = random_arg_name()
        self.__setitem__(name, item)
        return name


@dataclass
class State:
    imports: set[str] = field(default_factory=set)
    use_tz: bool = field(default_factory=lambda: settings.USE_TZ)
    extra_kwargs: RandomKeyDict = field(default_factory=RandomKeyDict)
    joins: list[str] = field(default_factory=list)
    skip_codegen: bool = False
    concrete: bool = False
