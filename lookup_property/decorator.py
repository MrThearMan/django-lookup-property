from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Unpack, overload

from .field import LookupPropertyDescriptor

if TYPE_CHECKING:
    from .typing import Callable, StateArgs

__all__ = [
    "lookup_property",
]


@overload
def lookup_property[R](__func: Callable[[], R], /) -> LookupPropertyDescriptor[R]: ...


@overload
def lookup_property[R](
    *,
    joins: list[str] | None = None,
    skip_codegen: bool | None = None,
    **kwargs: Unpack[StateArgs],
) -> Callable[[Callable[[], R]], LookupPropertyDescriptor[R]]: ...


def lookup_property[R](
    __func: Callable[[], R] | None = None,
    /,
    *,
    joins: list[str] | None = None,
    skip_codegen: bool | None = None,
    **kwargs: Unpack[StateArgs],
) -> LookupPropertyDescriptor[R] | Callable[[Callable[[], R]], LookupPropertyDescriptor[R]]:
    """Decorator for converting a class method to a LookupPropertyField"""
    if joins is not None:
        msg = "The `joins` argument is deprecated and does nothing. Joins are now added automatically."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)

    if skip_codegen is not None:
        msg = "The `skip_codegen` argument is deprecated and does nothing. Overrides skip codegen automatically."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)

    if __func is not None:
        return LookupPropertyDescriptor(__func)  # type: ignore[arg-type]

    def wrapper(__fn: Callable[[], R], /) -> LookupPropertyDescriptor[R]:
        return LookupPropertyDescriptor(__fn, **kwargs)  # type: ignore[arg-type]

    return wrapper
