from functools import wraps

from .typing import Callable, Concatenate, ParamSpec, Protocol, TypeVar, cast

__all__ = [
    "lookup_singledispatch",
]

T = TypeVar("T")
Str = TypeVar("Str", bound=str)
P = ParamSpec("P")


class RegisterFunc(Protocol[P, T, Str]):  # type: ignore[misc]
    def __call__(self, *, lookup: Str) -> Callable[[Callable[P, T]], Callable[P, T]]:
        pass


class Dispatch(Protocol[P, T, Str]):
    register: RegisterFunc[P, T, Str]

    def __call__(self, lookup: Str, *args: P.args, **kwargs: P.kwargs) -> T:
        pass


def lookup_singledispatch(func: Callable[Concatenate[Str, P], T]) -> Dispatch[P, T, Str]:
    registry: dict[str, Callable[P, T]] = {}

    def register(*, lookup: Str) -> Callable[[Callable[P, T]], Callable[P, T]]:
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

    wrapper = cast(Dispatch[P, T, Str], wrapper)
    wrapper.register = register
    return wrapper
