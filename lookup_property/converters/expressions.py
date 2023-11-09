import ast
from functools import singledispatch

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import Combinable, CombinedExpression

from ..typing import State
from .utils import ast_function, ast_property

__all__ = [
    "expression_to_ast",
]


@singledispatch
def expression_to_ast(expression: object, state: State) -> ast.AST:
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
def _(expression: list, state: State) -> ast.List:
    """Convert to lists: [..., ..., ...]"""
    return ast.List(
        elts=[expression_to_ast(value, state) for value in expression],
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: set, state: State) -> ast.Set:
    """Convert to sets: {..., ..., ...}"""
    return ast.Set(elts=[expression_to_ast(value, state) for value in expression])


@expression_to_ast.register
def _(expression: tuple, state: State) -> ast.Tuple:
    """Convert to tuples: (..., ..., ...)"""
    return ast.Tuple(elts=[expression_to_ast(value, state) for value in expression], ctx=ast.Load())


@expression_to_ast.register
def _(expression: dict, state: State) -> ast.Dict:
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
    Combinable.ADD: ast.Add(),
    Combinable.BITAND: ast.BitAnd(),
    Combinable.BITLEFTSHIFT: ast.LShift(),
    Combinable.BITOR: ast.BitOr(),
    Combinable.BITRIGHTSHIFT: ast.RShift(),
    Combinable.BITXOR: ast.BitXor(),
    Combinable.DIV: ast.Div(),
    Combinable.MOD: ast.Mod(),
    Combinable.MUL: ast.Mult(),
    Combinable.POW: ast.Pow(),
    Combinable.SUB: ast.Sub(),
}


@expression_to_ast.register
def _(expression: CombinedExpression, state: State) -> ast.BinOp | ast.Compare:
    """
    F("foo") * F("bar") -> self.foo * self.bar
    F("foo") + 2 -> self.foo + 2
    """
    left = expression_to_ast(expression.lhs, state)
    right = expression_to_ast(expression.rhs, state)

    bin_op = _BIN_OP_MAP.get(expression.connector)

    if bin_op is None:  # pragma: no cover
        msg = f"No implementation for connector '{expression.connector}'."
        raise ValueError(msg)

    return ast.BinOp(left=left, op=bin_op, right=right)
