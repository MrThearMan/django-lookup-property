import random
import string
from dataclasses import dataclass, field
from types import FunctionType
from typing import (
    Any,
    Callable,
    Collection,
    Concatenate,
    Generator,
    Iterable,
    Literal,
    NoReturn,
    ParamSpec,
    Protocol,
    Self,
    TypeVar,
    cast,
)

from django.conf import settings
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models.expressions import BaseExpression

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
Expr = BaseExpression | models.F | models.Q
ModelMethod = Callable[[TModel], Expr]
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
    joins: bool | list[str] = False
    skip_codegen: bool = False
    concrete: bool = False


class SelfNotUsable:  # pragma: no cover
    def __getattr__(self, item: Any) -> NoReturn:
        msg = "Lookup properties cannot use instance attributes. Refer to instance attributes with F() expressions."
        raise ValueError(msg)


SelfNotUsable = SelfNotUsable()
