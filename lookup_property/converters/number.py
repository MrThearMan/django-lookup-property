import ast

from django.db.models import functions

from ..typing import State
from .expressions import expression_to_ast


@expression_to_ast.register
def _(expression: functions.Chr, state: State) -> ast.Call:
    """Chr("foo") -> chr(self.foo)"""
    return ast.Call(
        func=ast.Name(id="chr", ctx=ast.Load()),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )
