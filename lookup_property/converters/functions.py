import ast

from django.db.models import functions
from django.db.models.functions import MD5, SHA1, SHA224, SHA256, SHA384, SHA512  # type: ignore[attr-defined]

from ..typing import Expr, State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: MD5 | SHA1 | SHA224 | SHA256 | SHA384 | SHA512, state: State) -> ast.Call:
    """
    MD5("foo") -> hashlib.md5(self.foo.encode()).hexdigest()
    SHA1("foo") -> hashlib.sha1(self.foo.encode()).hexdigest()
    SHA224("foo") -> hashlib.sha224(self.foo.encode()).hexdigest()
    SHA256("foo") -> hashlib.sha256(self.foo.encode()).hexdigest()
    SHA384("foo") -> hashlib.sha384(self.foo.encode()).hexdigest()
    SHA512("foo") -> hashlib.sha512(self.foo.encode()).hexdigest()
    """
    state.imports.add("hashlib")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="hashlib", ctx=ast.Load()),
                    attr=expression.__class__.__name__.lower(),
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=expression_to_ast(expression.lhs, state=state),
                            attr="encode",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ],
                keywords=[],
            ),
            attr="hexdigest",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Greatest, state: State) -> ast.Call:
    """Coalesce("foo", "bar") -> max({self.foo, self.bar}.difference({None}), default=None)"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="max", ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Set(elts=[expression_to_ast(arg, state=state) for arg in arguments]),
                    attr="difference",
                    ctx=ast.Load(),
                ),
                args=[ast.Set(elts=[ast.Constant(value=None)])],
                keywords=[],
            ),
        ],
        keywords=[
            ast.keyword(
                arg="default",
                value=ast.Constant(value=None),
            ),
        ],
    )


@expression_to_ast.register
def _(expression: functions.Least, state: State) -> ast.Call:
    """Coalesce("foo", "bar") -> min({self.foo, self.bar}.difference({None}), default=None)"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="min", ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Set(elts=[expression_to_ast(arg, state=state) for arg in arguments]),
                    attr="difference",
                    ctx=ast.Load(),
                ),
                args=[ast.Set(elts=[ast.Constant(value=None)])],
                keywords=[],
            ),
        ],
        keywords=[
            ast.keyword(
                arg="default",
                value=ast.Constant(value=None),
            ),
        ],
    )


@expression_to_ast.register
def _(expression: functions.JSONObject, state: State) -> ast.Dict:
    """JSONObject(foo=1) -> {'foo': 1}"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Dict(
        keys=[expression_to_ast(key, state) for key in arguments[::2]],
        values=[expression_to_ast(key, state) for key in arguments[1::2]],
    )


@expression_to_ast.register
def _(expression: functions.NullIf, state: State) -> ast.IfExp:
    """NullIf("foo", "bar") -> None if self.foo == self.bar else self.foo"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.IfExp(
        test=ast.Compare(
            left=expression_to_ast(arguments[0], state),
            ops=[ast.Eq()],
            comparators=[expression_to_ast(arguments[1], state)],
        ),
        body=ast.Constant(value=None),
        orelse=expression_to_ast(arguments[0], state),
    )
