import ast

from django.db import models  # noqa: TCH002
from django.db.models import aggregates
from django.db.models.expressions import Star

from ..typing import State
from .expressions import expression_to_ast
from .utils import ast_function, ast_method


@expression_to_ast.register
def _(expression: aggregates.Count, state: State) -> ast.Call:  # pragma: no cover
    """
    1) if state.aggregate_is_to_many is True:

    1a) Count("relation") -> len(self.relation.all())

    1b) def foo():
            return Count("relation", filter=Q(relation__foo=1))
    ->  def foo(random_key=Q(relation__foo=1)):
            return len(self.relation.filter(random_key()))

    ---------------------------------------------------------

    2) if state.aggregate_is_to_many is False:

    2a) Count("pk") -> len(self.__class__.all())

    2b) def foo():
            return Count("pk", filter=Q(pk__gt=10))
    ->  def foo(random_key=Q(pk__gt=10)):
            return len(self.__class__.filter(random_key()))
    """
    arg: models.F | Star = expression.source_expressions[0]  # type: ignore[assignment]

    args: list[ast.Call] = []
    if expression.filter is not None:
        args.append(ast_function(state.extra_kwargs.add(lambda: expression.filter)))

    return ast.Call(
        func=ast.Name(id="len", ctx=ast.Load()),
        args=[
            ast_method(
                "all" if expression.filter is None else "filter",
                [arg.name] if state.aggregate_is_to_many and not isinstance(arg, Star) else ["__class__", "objects"],
                *args,
            ),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: aggregates.Max | aggregates.Min, state: State) -> ast.Call:  # pragma: no cover
    """
    1) Max("field") -> max(self.__class__.objects.values_list("field", flat=True).all(), default=None)
       Min("field") -> min(self.__class__.objects.values_list("field", flat=True).all(), default=None)

    ---------------------------------------------------------

    2) Max("field", default=1) -> max(self.__class__.objects.values_list("field", flat=True).all(), default=1)
       Min("field", default=1) -> min(self.__class__.objects.values_list("field", flat=True).all(), default=1)

    ---------------------------------------------------------

    3) def foo():
           return Max("field", filter=Q(field__gt=1))
    -> def foo(random_key=Q(field__gt=1)):
           return max(self.__class__.objects.values_list("field", flat=True).filter(random_key()), default=None)

       def foo():
           return Min("field", filter=Q(field__gt=1))
    -> def foo(random_key=Q(field__gt=1)):
           return min(self.__class__.objects.values_list("field", flat=True).filter(random_key()), default=None)
    """
    arg: models.F = expression.source_expressions[0]  # type: ignore[assignment]

    args: list[ast.Call] = []
    if expression.filter is not None:
        args.append(ast_function(state.extra_kwargs.add(lambda: expression.filter)))

    return ast.Call(
        func=ast.Name(id=expression.name.lower(), ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast_method(
                        "values_list",
                        ["__class__", "objects"],
                        ast.Constant(value=arg.name),
                        flat=ast.Constant(value=True),
                    ),
                    attr="all" if expression.filter is None else "filter",
                    ctx=ast.Load(),
                ),
                args=args,
                keywords=[],
            )
        ],
        keywords=[
            ast.keyword(arg="default", value=expression_to_ast(expression.default, state=state)),
        ],
    )


@expression_to_ast.register
def _(expression: aggregates.Sum, state: State) -> ast.Call:  # pragma: no cover
    """
    1) if state.aggregate_is_to_many is True:

    1a) Sum("relation") -> sum(self.relation.all())

    1b) def foo():
            return Sum("relation", filter=Q(relation__foo=1))
    ->  def foo(random_key=Q(relation__foo=1)):
            return sum(self.relation.filter(random_key()))

    ---------------------------------------------------------

    2) if state.aggregate_is_to_many is False:

    2a) Sum("field") -> sum(self.__class__.objects.values_list("field", flat=True).all())

    2b) def foo():
            return Sum("field", filter=Q(pk__gt=10))
    ->  def foo(random_key=Q(pk__gt=10)):
            return sum(self.__class__.values_list("field", flat=True).filter(random_key()))

    """
    arg: models.F = expression.source_expressions[0]  # type: ignore[assignment]

    args: list[ast.Call] = []
    if expression.filter is not None:
        args.append(ast_function(state.extra_kwargs.add(lambda: expression.filter)))

    return ast.Call(
        func=ast.Name(id="sum", ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast_method(
                        "values_list",
                        ["__class__", "objects"],
                        ast.Constant(value=arg.name),
                        flat=ast.Constant(value=True),
                    ),
                    attr="all" if expression.filter is None else "filter",
                    ctx=ast.Load(),
                ),
                args=args,
                keywords=[],
            )
        ],
        keywords=[],
    )


# TODO: Avg, StdDev, Variance
