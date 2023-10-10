import ast
from functools import singledispatch

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import CombinedExpression

from ..typing import Any, State
from .utils import ast_function, ast_property

__all__ = [
    "expression_to_ast",
]


@singledispatch
def expression_to_ast(expression: Any, state: State) -> ast.AST:  # pragma: no cover
    msg = f"No implementation for expression '{expression}'."
    raise ValueError(msg)


@expression_to_ast.register
def _(expression: object, state: State) -> ast.Call:
    """
    Default converter for all objects, which works by setting a new keyword argument:

    def func(self):
        return Q(foo=datetime.date(2000, 1, 1))

    ->

    def foo(self, random_string=lambda: datetime.date(2000, 1, 1)):
        return self.foo == random_string()
    """
    arg = state.extra_kwargs.add(lambda: expression)
    return ast_function(arg)


@expression_to_ast.register
def _(expression: None | str | int | float | bool | bytes, state: State) -> ast.Constant:  # noqa: PYI041
    """Convert builtin values to constants"""
    return ast.Constant(value=expression)


@expression_to_ast.register
def _(expression: list, state: State) -> ast.List:  # pragma: no cover
    """Convert to lists: [..., ..., ...]"""
    return ast.List(
        elts=[expression_to_ast(value, state) for value in expression],
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: set, state: State) -> ast.Set:  # pragma: no cover
    """Convert to sets: {..., ..., ...}"""
    return ast.Set(elts=[expression_to_ast(value, state) for value in expression])


@expression_to_ast.register
def _(expression: tuple, state: State) -> ast.Tuple:  # pragma: no cover
    """Convert to tuples: (..., ..., ...)"""
    return ast.Tuple(elts=[expression_to_ast(value, state) for value in expression], ctx=ast.Load())


@expression_to_ast.register
def _(expression: dict, state: State) -> ast.Dict:  # pragma: no cover
    """Convert to dicts: {...: ..., ...: ...}"""
    return ast.Dict(
        keys=[expression_to_ast(key, state) for key in expression],
        values=[expression_to_ast(value, state) for value in expression.values()],
    )


@expression_to_ast.register
def _(expression: models.Value, state: State) -> ast.AST:
    """Value("foo") -> "foo"""
    return expression_to_ast(expression.value, state)


@expression_to_ast.register
def _(expression: models.F, state: State) -> ast.Attribute:
    """
    F("foo") -> self.foo
    F("foo__bar") -> self.foo.bar
    """
    return ast_property(*expression.name.split(LOOKUP_SEP))


_BIN_OP_MAP: dict[str, ast.operator] = {
    "+": ast.Add(),
    "&": ast.BitAnd(),
    "|": ast.BitOr(),
    "^": ast.BitXor(),
    "/": ast.Div(),
    "//": ast.FloorDiv(),
    "<<": ast.LShift(),
    "%": ast.Mod(),
    "*": ast.Mult(),
    "@": ast.MatMult(),
    "**": ast.Pow(),
    ">>": ast.RShift(),
    "-": ast.Sub(),
}

_COMP_OP_MAP: dict[str, ast.cmpop] = {  # type: ignore[assignment]
    "=": ast.Eq(),
    ">": ast.Gt(),
    ">=": ast.GtE(),
    "in": ast.In(),
    "is": ast.Is(),
    "is not": ast.IsNot(),
    "<": ast.Lt(),
    "<=": ast.LtE(),
    "!=": ast.NotEq(),
    "not in": ast.NotIn(),
}


@expression_to_ast.register
def _(expression: CombinedExpression, state: State) -> ast.BinOp | ast.Compare:
    """
    F("foo") * F("bar") -> self.foo * self.bar
    F("foo") + Value(2) -> self.foo + 2
    """
    left = expression_to_ast(expression.lhs, state)
    right = expression_to_ast(expression.rhs, state)

    bin_op = _BIN_OP_MAP.get(expression.connector)
    comp_op = _COMP_OP_MAP.get(expression.connector)

    if bin_op is None and comp_op is None:  # pragma: no cover
        msg = f"No implementation for connector '{expression.connector}'."
        raise ValueError(msg)

    if bin_op is not None:
        return ast.BinOp(left=left, op=bin_op, right=right)

    return ast.Compare(left=left, ops=[comp_op], comparators=[right])  # pragma: no cover
