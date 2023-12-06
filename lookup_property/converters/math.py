import ast

from django.db.models import functions
from django.db.models.functions.math import Random  # type: ignore[attr-defined]

from ..typing import Expr, State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: functions.Abs, state: State) -> ast.Call:
    """Abs("foo") -> abs(self.foo)"""
    return ast.Call(
        func=ast.Name(id="abs", ctx=ast.Load()),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(
    expression: (
        functions.ACos
        | functions.ASin
        | functions.ATan
        | functions.Ceil
        | functions.Cos
        | functions.Degrees
        | functions.Exp
        | functions.Floor
        | functions.Radians
        | functions.Sin
        | functions.Sqrt
        | functions.Tan
    ),
    state: State,
) -> ast.Call:
    """
    ACos("foo") -> math.acos(self.foo)
    Ceil("foo") -> math.ceil(self.foo)
    etc.
    """
    state.imports.add("math")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr=expression.__class__.__name__.lower(),
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Cot, state: State) -> ast.BinOp:
    """Cot("foo") -> 1 / math.tan(self.foo)"""
    state.imports.add("math")
    return ast.BinOp(
        left=ast.Constant(value=1),
        op=ast.Div(),
        right=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="math", ctx=ast.Load()),
                attr="tan",
                ctx=ast.Load(),
            ),
            args=[
                expression_to_ast(expression.lhs, state=state),
            ],
            keywords=[],
        ),
    )


@expression_to_ast.register
def _(expression: functions.Pi, state: State) -> ast.Attribute:
    """Pi() -> math.pi"""
    state.imports.add("math")
    return ast.Attribute(
        value=ast.Name(id="math", ctx=ast.Load()),
        attr="pi",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Power, state: State) -> ast.Call:
    """Power("foo", 3) -> math.pow(self.foo, 3)"""
    state.imports.add("math")
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr="pow",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[0], state=state),
            expression_to_ast(arguments[1], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.ATan2 | functions.Log, state: State) -> ast.Call:
    """
    ATan2("foo", 3) -> math.atan2(self.foo, 3)
    Log("foo", 10) -> math.log(self.foo, 10)
    """
    state.imports.add("math")
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr=expression.__class__.__name__.lower(),
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[0], state=state),
            expression_to_ast(arguments[1], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Ln, state: State) -> ast.Call:
    """Ln("foo") -> math.log(self.foo)  # default base is 'e' (=ln)"""
    state.imports.add("math")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr="log",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Mod, state: State) -> ast.BinOp:
    """Mod("foo", 4) -> self.foo % 4"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.BinOp(
        left=expression_to_ast(arguments[0], state=state),
        op=ast.Mod(),
        right=expression_to_ast(arguments[1], state=state),
    )


@expression_to_ast.register
def _(expression: Random, state: State) -> ast.Call:
    """Random() -> random.random()"""
    state.imports.add("random")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="random", ctx=ast.Load()),
            attr="random",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Round, state: State) -> ast.Call:
    """
    Round("foo") -> round(self.foo)
    Round("foo", precision=2) -> round(self.foo, 2)
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="round", ctx=ast.Load()),
        args=[expression_to_ast(arg, state=state) for arg in arguments],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Sign, state: State) -> ast.BinOp:
    """Sign("foo") -> int(self.foo > 0) - int(self.foo < 0)  # -1 or 0 or 1"""
    return ast.BinOp(
        left=ast.Call(
            func=ast.Name(id="int", ctx=ast.Load()),
            args=[
                ast.Compare(
                    left=expression_to_ast(expression.lhs, state=state),
                    ops=[ast.Gt()],
                    comparators=[ast.Constant(value=0)],
                ),
            ],
            keywords=[],
        ),
        op=ast.Sub(),
        right=ast.Call(
            func=ast.Name(id="int", ctx=ast.Load()),
            args=[
                ast.Compare(
                    left=expression_to_ast(expression.lhs, state=state),
                    ops=[ast.Lt()],
                    comparators=[ast.Constant(value=0)],
                ),
            ],
            keywords=[],
        ),
    )
