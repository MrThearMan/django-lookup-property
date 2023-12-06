import ast

from ..typing import Iterable

__all__ = [
    "ast_attribute",
    "ast_function",
    "ast_method",
    "ast_property",
]


def ast_function(func_name: str, attrs: Iterable[str] = (), *args: ast.AST, **kwargs: ast.AST) -> ast.Call:
    """
    Transform given attributes and function name to a function call ast node.

    (func=foo, attrs=[]) -> foo()
    (func=foo, attrs=["bar"]) -> bar.foo()
    (func=foo, attrs=["foo", "bar"]) -> foo.bar.foo()
    (func=foo, attrs=["bar"], Expr) -> bar.foo(Expr)
    (func=foo, attrs=["bar"], fizz=Expr) -> bar.foo(fizz=Expr)
    """
    return ast.Call(
        func=ast_attribute(*attrs, func_name),
        args=list(args),
        keywords=[ast.keyword(arg=key, value=value) for key, value in kwargs.items()],
    )


def ast_attribute(*attrs: str) -> ast.Attribute:
    """
    Transform given attributes to an attribute ast node.

    ["self", "bar"] -> self.bar
    ["foo", "foo", "bar"] -> foo.foo.bar
    """
    value: ast.Name | ast.Attribute | None = None
    for i, name in enumerate(attrs):
        if i == 0:
            value = ast.Name(id=name, ctx=ast.Load())
            continue
        value = ast.Attribute(value=value, attr=name, ctx=ast.Load())
    return value  # type: ignore[return-value]


def ast_method(func_name: str, attrs: Iterable[str] = (), *args: ast.AST, **kwargs: ast.AST) -> ast.Call:
    """
    Transform given attributes and function name to a class instance method ast node.

    (func=foo, attrs=[]) -> self.foo()
    (func=foo, attrs=["bar"]) -> self.bar.foo()
    (func=foo, attrs=["foo", "bar"]) -> self.foo.bar.foo()
    (func=foo, attrs=["bar"], Expr) -> self.bar.foo(Expr)
    (func=foo, attrs=["bar"], fizz=Expr) -> self.bar.foo(fizz=Expr)
    """
    return ast_function(func_name, ("self", *attrs), *args, **kwargs)


def ast_property(*attrs: str) -> ast.Attribute:
    """
    Transform given attributes to a class instance attribute/property ast node.

    ["foo"] -> self.foo
    ["foo", "foo", "bar"] -> self.foo.foo.bar
    """
    return ast_attribute("self", *attrs)
