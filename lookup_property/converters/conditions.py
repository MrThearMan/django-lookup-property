import ast
from typing import cast

from django.db import models
from django.db.models import functions

from ..typing import Expr, State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: models.Case, state: State) -> ast.If:
    """
    Case(When(condition=Q(fizz=True), then=Value("foo")), default=Value("bar")))

    ->

    if self.fizz == True:
        return "foo"
    else:
        return "bar"
    """
    cases: list[models.When] = expression.cases.copy()
    default = expression_to_ast(expression.default, state=state)
    if not isinstance(default, ast.If):
        default = ast.Return(value=default)
    default = cast(ast.Return | ast.If, default)
    return cases_to_if_statement(cases, default, state=state)


def cases_to_if_statement(cases: list[models.When], default: ast.Return | ast.If, state: State) -> ast.If:
    """Recursively convert the When expressions of a Case expression to an if statement."""
    case = cases.pop(0)
    statement = cases_to_if_statement(cases, default, state=state) if cases else default
    value = expression_to_ast(case.result, state=state)
    if not isinstance(value, ast.If):
        value = ast.Return(value=value)
    return ast.If(
        test=expression_to_ast(case.condition, state=state),
        body=[value],
        orelse=[statement],
    )


@expression_to_ast.register
def _(expression: functions.Coalesce, state: State) -> ast.If:
    """
    Coalesce("foo", "bar)

    ->

    if self.foo is not None:
        return self.foo
    elif self.bar is not None:
        return self.bar
    else:
        return None
    """
    arguments: list[Expr] = expression.get_source_expressions().copy()
    return args_to_if_statement(arguments, state=state)


def args_to_if_statement(args: list[Expr], state: State) -> ast.If:
    arg = args.pop(0)
    statement = args_to_if_statement(args, state=state) if args else ast.Return(value=ast.Constant(value=None))
    value = expression_to_ast(arg, state=state)
    return ast.If(
        test=ast.Compare(
            left=value,
            ops=[ast.IsNot()],
            comparators=[ast.Constant(value=None)],
        ),
        body=[ast.Return(value=value)],
        orelse=[statement],
    )
