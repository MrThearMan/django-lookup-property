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
