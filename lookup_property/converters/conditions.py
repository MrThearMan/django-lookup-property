import ast

from django.db import models
from django.db.models import functions

from ..typing import Expr, State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: models.Case, state: State) -> ast.IfExp:
    """
    Case(When(condition=Q(fizz=True), then=Value("foo")), default=Value("bar")))
    -> if "foo" self.fizz == True else "bar"
    """
    cases: list[models.When] = expression.cases.copy()
    default = expression_to_ast(expression.default, state=state)
    return cases_to_if_expression(cases, default, state=state)


def cases_to_if_expression(cases: list[models.When], default: ast.AST, state: State) -> ast.IfExp:
    """Recursively convert the When expressions of a Case expression to an if expression."""
    case = cases.pop(0)
    statement = cases_to_if_expression(cases, default, state=state) if cases else default
    return ast.IfExp(
        test=expression_to_ast(case.condition, state=state),
        body=expression_to_ast(case.result, state=state),
        orelse=statement,
    )


@expression_to_ast.register
def _(expression: functions.Coalesce, state: State) -> ast.IfExp:
    """
    Coalesce("foo", "bar)
    -> self.foo if self.foo is not None else self.bar if self.bar is not None else None
    """
    arguments: list[Expr] = expression.get_source_expressions().copy()
    return args_to_if_expression(arguments, state=state)


def args_to_if_expression(args: list[Expr], state: State) -> ast.IfExp:
    arg = args.pop(0)
    statement = args_to_if_expression(args, state=state) if args else ast.Constant(value=None)
    value = expression_to_ast(arg, state=state)
    return ast.IfExp(
        test=ast.Compare(
            left=value,
            ops=[ast.IsNot()],
            comparators=[ast.Constant(value=None)],
        ),
        body=value,
        orelse=statement,
    )
