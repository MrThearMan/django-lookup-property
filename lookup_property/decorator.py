from __future__ import annotations

from typing import TYPE_CHECKING, Unpack, overload

from .field import LookupPropertyDescriptor

if TYPE_CHECKING:
    from .typing import Callable, R, StateArgs

__all__ = [
    "lookup_property",
]


@overload
def lookup_property(__func: Callable[[], R], /) -> LookupPropertyDescriptor[R]: ...


@overload
def lookup_property(**kwargs: Unpack[StateArgs]) -> Callable[[Callable[[], R]], LookupPropertyDescriptor[R]]: ...


def lookup_property(
    __func: Callable[[], R] | None = None,
    /,
    **kwargs: Unpack[StateArgs],
) -> LookupPropertyDescriptor[R] | Callable[[Callable[[], R]], LookupPropertyDescriptor[R]]:
    """Decorator for converting a class method to a LookupPropertyField"""
    if __func is not None:
        return LookupPropertyDescriptor(__func)  # type: ignore[arg-type]

    def wrapper(__fn: Callable[[], R], /) -> R:
        return LookupPropertyDescriptor(__fn, **kwargs)  # type: ignore[arg-type]

    return wrapper
