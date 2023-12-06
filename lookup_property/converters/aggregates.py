import ast

from django.db.models import aggregates

from ..typing import State
from .expressions import expression_to_ast
from .utils import ast_function, ast_method


@expression_to_ast.register
def _(
    expression: (
        aggregates.Count
        | aggregates.Max
        | aggregates.Min
        | aggregates.Sum
        | aggregates.Avg
        | aggregates.StdDev
        | aggregates.Variance
    ),
    state: State,
) -> ast.Subscript:
    """
       def foo():
           return Max("field", default=0, filter=Q(field__gt=10))

    -> def foo(random_string=lambda: Max("field", default=0, filter=Q(field__gt=10))):
           return self.__class__.objects.aggregate(random_string=random_string())["random_string"]
    """
    arg_name = state.extra_kwargs.add(lambda: expression)

    return ast.Subscript(
        value=ast_method(
            "aggregate",
            ["__class__", "objects"],
            **{arg_name: ast_function(arg_name)},
        ),
        slice=ast.Constant(value=arg_name),
        ctx=ast.Load(),
    )


try:  # pragma: no cover
    from django.contrib.postgres import aggregates as pg_aggregates

    @expression_to_ast.register
    def _(
        expression: (
            pg_aggregates.ArrayAgg
            | pg_aggregates.BitAnd
            | pg_aggregates.BitOr
            | pg_aggregates.BitXor
            | pg_aggregates.BoolAnd
            | pg_aggregates.BoolOr
            | pg_aggregates.JSONBAgg
            | pg_aggregates.StringAgg
            | pg_aggregates.StatAggregate
            | pg_aggregates.Corr
            | pg_aggregates.CovarPop
            | pg_aggregates.RegrAvgX
            | pg_aggregates.RegrAvgY
            | pg_aggregates.RegrCount
            | pg_aggregates.RegrIntercept
            | pg_aggregates.RegrR2
            | pg_aggregates.RegrSlope
            | pg_aggregates.RegrSXX
            | pg_aggregates.RegrSXY
            | pg_aggregates.RegrSYY
        ),
        state: State,
    ) -> ast.Subscript:
        arg_name = state.extra_kwargs.add(lambda: expression)

        return ast.Subscript(
            value=ast_method(
                "aggregate",
                ["__class__", "objects"],
                **{arg_name: ast_function(arg_name)},
            ),
            slice=ast.Constant(value=arg_name),
            ctx=ast.Load(),
        )

except ModuleNotFoundError:
    pass
