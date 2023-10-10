import ast

from django.db.models import functions

from ..typing import Expr, State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: functions.Concat, state: State) -> ast.AST:
    """
    Used together with the ConcatPair-converter below to concatenate values in pairs:
    Concat(F("foo"), Value(" "), F("bar")) -> self.foo + ("" + self.bar)
    """
    source_expressions = expression.get_source_expressions()
    return expression_to_ast(source_expressions[0], state)


@expression_to_ast.register
def _(expression: functions.ConcatPair, state: State) -> ast.BinOp:
    """Concat(F("foo"), F("bar")) -> self.foo + self.bar"""
    source_expressions = expression.get_source_expressions()
    left = expression_to_ast(source_expressions[0], state)
    right = expression_to_ast(source_expressions[1], state)
    return ast.BinOp(left=left, op=ast.Add(), right=right)


@expression_to_ast.register
def _(expression: functions.Upper, state: State) -> ast.Call:
    """Upper("foo") -> self.foo.upper()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="upper",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Lower, state: State) -> ast.Call:
    """Lower("foo") -> self.foo.lower()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="lower",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.LPad, state: State) -> ast.Call:
    """LPad("foo", length=20, fill_text=".") -> self.foo.rjust(20, ".")"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="rjust",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.RPad, state: State) -> ast.Call:
    """RPad("foo", length=20, fill_text=".") -> self.foo.ljust(20, ".")"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="ljust",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.RTrim, state: State) -> ast.Call:
    """RTrim("foo") -> self.foo.rstrip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="rstrip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.LTrim, state: State) -> ast.Call:
    """LTrim("foo") -> self.foo.lstrip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="lstrip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Length, state: State) -> ast.Call:
    """Length("foo") -> len(self.foo)"""
    return ast.Call(
        func=ast.Name(id="len", ctx=ast.Load()),
        args=[expression_to_ast(expression.lhs, state=state)],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Left, state: State) -> ast.Subscript:
    """Left("foo", length=1) -> self.foo[:1]"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=None,
            upper=expression_to_ast(arguments[1], state=state),
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Right, state: State) -> ast.Subscript:
    """Right("foo", length=1) -> self.foo[-1:]"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=ast.UnaryOp(
                op=ast.USub(),
                operand=expression_to_ast(arguments[1], state=state),
            ),
            upper=None,
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Repeat, state: State) -> ast.BinOp:
    """Repeat("foo", length=3) -> self.foo * 3"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.BinOp(
        left=expression_to_ast(arguments[0], state=state),
        op=ast.Mult(),
        right=expression_to_ast(arguments[1], state=state),
    )


@expression_to_ast.register
def _(expression: functions.Replace, state: State) -> ast.Call:
    """Replace("foo", text=Value("oo"), replacement=Value("uu")) -> self.foo.replace('oo', 'uu')"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="replace",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Reverse, state: State) -> ast.Subscript:
    """Reverse("foo") -> self.foo[::-1]"""
    return ast.Subscript(
        value=expression_to_ast(expression.lhs, state=state),
        slice=ast.Slice(
            lower=None,
            upper=None,
            step=ast.UnaryOp(
                op=ast.USub(),
                operand=ast.Constant(value=1),
            ),
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.StrIndex, state: State) -> ast.If:
    """
    StrIndex("foo", Value("o"))

    ->

    if 'o' in self.foo:
        return self.foo.index('o') + 1
    else:
        return 0
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.If(
        test=ast.Compare(
            left=expression_to_ast(arguments[1], state=state),
            ops=[ast.In()],
            comparators=[expression_to_ast(arguments[0], state=state)],
        ),
        body=[
            ast.Return(
                value=ast.BinOp(
                    left=ast.Call(
                        func=ast.Attribute(
                            value=expression_to_ast(arguments[0], state=state),
                            attr="index",
                            ctx=ast.Load(),
                        ),
                        args=[expression_to_ast(arguments[1], state=state)],
                        keywords=[],
                    ),
                    op=ast.Add(),
                    right=ast.Constant(value=1),
                ),
            ),
        ],
        orelse=[
            ast.Return(value=ast.Constant(value=0)),
        ],
    )


@expression_to_ast.register
def _(expression: functions.Substr, state: State) -> ast.Subscript:
    """
    Substr("foo", x) -> self.foo[x - 1:]
    Substr("foo", x, y) -> self.foo[x - 1:x + y - 1]
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=ast.BinOp(
                left=expression_to_ast(arguments[1], state),
                op=ast.Sub(),
                right=ast.Constant(value=1),
            ),
            upper=(
                ast.BinOp(
                    left=ast.BinOp(
                        left=expression_to_ast(arguments[1], state),
                        op=ast.Add(),
                        right=expression_to_ast(arguments[2], state),
                    ),
                    op=ast.Sub(),
                    right=ast.Constant(value=1),
                )
                if len(arguments) == 3  # noqa: PLR2004
                else None
            ),
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Trim, state: State) -> ast.Call:
    """Trim("foo") -> self.foo.strip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="strip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Ord, state: State) -> ast.Call:
    """Ord("foo") -> ord(self.foo)"""
    return ast.Call(
        func=ast.Name(id="ord", ctx=ast.Load()),
        args=[
            ast.Subscript(
                value=expression_to_ast(expression.lhs, state=state),
                slice=ast.Constant(value=0),
                ctx=ast.Load(),
            ),
        ],
        keywords=[],
    )
