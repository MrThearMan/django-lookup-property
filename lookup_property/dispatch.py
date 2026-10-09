from __future__ import annotations

from functools import wraps

from .typing import Callable, Concatenate, Protocol, cast

__all__ = [
    "lookup_singledispatch",
]


class RegisterFunc[**P, T, Str: str](Protocol):
    def __call__(self, *, lookup: Str | None) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


class Dispatch[**P, T, Str: str](Protocol):
    register: RegisterFunc[P, T, Str]

    def __call__(self, lookup: Str, *args: P.args, **kwargs: P.kwargs) -> T: ...


def lookup_singledispatch[Str: str, **P, T](func: Callable[Concatenate[Str, P], T]) -> Dispatch[P, T, Str]:
    registry: dict[str | None, Callable[P, T]] = {}

    def register(*, lookup: Str | None) -> Callable[[Callable[P, T]], Callable[P, T]]:
        def decorator(impl_func: Callable[P, T]) -> Callable[P, T]:
            registry[lookup] = impl_func
            return impl_func

        return decorator

    @wraps(func)
    def wrapper(lookup: Str, *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            impl = registry[lookup]
        except KeyError:
            return func(lookup, *args, **kwargs)

        return impl(*args, **kwargs)

    dispatch = cast("Dispatch[P, T, Str]", wrapper)
    dispatch.register = register
    return dispatch
