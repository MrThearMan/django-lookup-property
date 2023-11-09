import ast
from functools import singledispatch

from django.db import models
from django.db.models import functions

from ..typing import Expr, State
from .expressions import expression_to_ast

__all__ = [
    "convert_django_field",
]


@expression_to_ast.register
def _(expression: functions.Cast, state: State) -> ast.Call:
    """
    Cast("foo", output_field=IntegerField()) -> int(self.foo)
    Cast("foo", output_field=CharField()) -> str(self.foo)
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=convert_django_field(expression.output_field, state=state),
        args=[expression_to_ast(arguments[0], state=state)],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: models.ExpressionWrapper, state: State) -> ast.Call:
    """
    ExpressionWrapper(F("foo") - 2, output_field=IntegerField()) -> int(self.foo - 2)
    ExpressionWrapper(F("foo") * f("bar"), output_field=CharField()) -> str(self.foo + self.bar)
    """
    return ast.Call(
        func=convert_django_field(expression.output_field, state=state),
        args=[expression_to_ast(expression.expression, state=state)],
        keywords=[],
    )


@singledispatch
def convert_django_field(field: models.Field, state: State) -> ast.Name | ast.Attribute:
    msg = f"No implementation for field '{field.__class__.__name__}'."
    raise ValueError(msg)


@convert_django_field.register
def _(
    field: (
        models.CharField
        | models.TextField
        | models.EmailField
        | models.SlugField
        | models.URLField
        | models.GenericIPAddressField
        | models.FileField
        | models.FilePathField
    ),
    state: State,
) -> ast.Name:
    """Cast("foo", output_field=CharField()) -> str(self.foo)"""
    return ast.Name(id="str", ctx=ast.Load())


@convert_django_field.register
def _(
    field: (
        models.IntegerField
        | models.BigIntegerField
        | models.PositiveIntegerField
        | models.PositiveSmallIntegerField
        | models.SmallIntegerField
    ),
    state: State,
) -> ast.Name:
    """Cast("foo", output_field=IntegerField()) -> int(self.foo)"""
    return ast.Name(id="int", ctx=ast.Load())


@convert_django_field.register
def _(field: models.FloatField | models.DurationField, state: State) -> ast.Name:
    """Cast("foo", output_field=FloatField()) -> float(self.foo)"""
    return ast.Name(id="float", ctx=ast.Load())


@convert_django_field.register
def _(field: models.BooleanField | models.NullBooleanField, state: State) -> ast.Name:
    """Cast("foo", output_field=BooleanField()) -> bool(self.foo)"""
    return ast.Name(id="bool", ctx=ast.Load())


@convert_django_field.register
def _(field: models.DecimalField, state: State) -> ast.Attribute:
    """Cast("foo", output_field=DecimalField()) -> decimal.Decimal(self.foo)"""
    state.imports.add("decimal")
    return ast.Attribute(
        value=ast.Name(id="decimal", ctx=ast.Load()),
        attr="Decimal",
        ctx=ast.Load(),
    )


@convert_django_field.register
def _(field: models.UUIDField, state: State) -> ast.Attribute:
    """Cast("foo", output_field=UUIDField()) -> uuid.UUID(self.foo)"""
    state.imports.add("uuid")
    return ast.Attribute(
        value=ast.Name(id="uuid", ctx=ast.Load()),
        attr="UUID",
        ctx=ast.Load(),
    )


@convert_django_field.register
def _(field: models.JSONField, state: State) -> ast.Attribute:
    """Cast("foo", output_field=JSONField()) -> json.loads(self.foo)"""
    state.imports.add("json")
    return ast.Attribute(
        value=ast.Name(id="json", ctx=ast.Load()),
        attr="loads",
        ctx=ast.Load(),
    )


try:  # pragma: no cover
    from django.contrib.postgres.fields import ArrayField, HStoreField

    @convert_django_field.register
    def _(field: ArrayField, state: State) -> ast.Name:
        """Cast("foo", output_field=ArrayField()) -> list(self.foo)"""
        return ast.Name(id="list", ctx=ast.Load())

    @convert_django_field.register
    def _(field: HStoreField, state: State) -> ast.Name:
        """Cast("foo", output_field=HStoreField()) -> dict(self.foo)"""
        return ast.Name(id="dict", ctx=ast.Load())

except ModuleNotFoundError:
    pass
