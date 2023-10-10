import ast
from typing import Any

from django.db import models
from django.db.models import lookups
from django.db.models.constants import LOOKUP_SEP

from ..dispatch import lookup_singledispatch
from ..typing import InstanceAttribute, State
from .expressions import expression_to_ast

__all__ = [
    "lookup_to_ast",
]


@expression_to_ast.register
def _(expression: models.Q, state: State) -> ast.Name | ast.BoolOp | ast.UnaryOp | ast.AST:
    """
    Convert Q-Nodes to boolean comparisons, examples:
    Q(foo=1) -> self.foo == 1
    Q(foo__in=[1, 2]) -> self.foo in [1, 2]
    """
    children: list[tuple[str, Any]] = expression.children  # type: ignore[assignment]
    comparison: ast.Name | ast.BoolOp | ast.AST

    if not children:
        comparison = ast.Name(id="True", ctx=ast.Load())

    elif len(children) == 1:
        comparison = to_and_or_comparison(attr=children[0][0], value=children[0][1], state=state)

    elif expression.connector in (models.Q.OR, models.Q.AND):
        comparison = ast.BoolOp(
            op=ast.Or() if expression.connector == models.Q.OR else ast.And(),
            values=[to_and_or_comparison(attr=attr, value=value, state=state) for attr, value in children],
        )

    else:  # models.Q.XOR
        comparison = to_xor_comparison(children=children, state=state)

    if expression.negated:
        return ast.UnaryOp(op=ast.Not(), operand=comparison)

    return comparison


def to_xor_comparison(children: list[tuple[str, Any]], state: State) -> ast.BinOp:
    """Q(foo__in=[...]) ^ Q(bar=1) -> (self.foo in [...]) ^ (self.bar == 1)"""
    right = children[-1]

    left: ast.AST
    if len(children) == 2:  # noqa: PLR2004
        left = to_and_or_comparison(children[0][0], children[0][1], state)
    else:
        left = to_xor_comparison(children[:-1], state)

    return ast.BinOp(
        left=left,
        op=ast.BitXor(),
        right=to_and_or_comparison(right[0], right[1], state),
    )


def to_and_or_comparison(attr: str, value: Any, state: State) -> ast.AST:
    """
    Q(foo=1) | Q(bar=2) -> self.foo == 1 or self.bar == 2
    Q(foo=1) & Q(bar=2) -> self.foo == 1 and self.bar == 2
    """
    attrs = attr.split(LOOKUP_SEP)
    if len(attrs) == 1:
        return lookup_to_ast("exact", attrs, value, state)

    return lookup_to_ast(attrs[-1], attrs[:-1], value, state)


@lookup_singledispatch
def lookup_to_ast(lookup: str, attrs: list[str], value: Any, state: State) -> ast.AST:
    msg = f"No implementation for '{lookup}' ({LOOKUP_SEP.join(attrs)}{LOOKUP_SEP}{lookup}={value!r})."
    raise ValueError(msg)


@lookup_to_ast.register(lookup=lookups.Exact.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """
    Q(foo="bar") -> self.foo == "bar"
    Q(foo__exact="bar") -> self.foo == "bar"
    """
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.Eq()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.IExact.lookup_name)
def _(attrs: list[str], value: str | None, state: State) -> ast.AST | ast.Compare:
    """Q(foo__iexact="bar") -> self.foo.casefold() == "bar".casefold()"""
    if value is None:
        return lookup_to_ast("exact", attrs, value, state)

    return ast.Compare(
        left=ast.Call(
            func=ast.Attribute(
                value=InstanceAttribute(attrs=attrs),
                attr="casefold",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        ),
        ops=[ast.Eq()],
        comparators=[
            ast.Call(
                func=ast.Attribute(
                    value=expression_to_ast(value, state),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        ],
    )


@lookup_to_ast.register(lookup=lookups.GreaterThan.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """Q(foo__gt=1) -> self.foo > 1"""
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.Gt()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.GreaterThanOrEqual.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """Q(foo__gte=1) -> self.foo >= 1"""
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.GtE()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.LessThan.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """Q(foo__lt=1) -> self.foo < 1"""
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.Lt()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.LessThanOrEqual.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """Q(foo__lte=1) -> self.foo <= 1"""
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.LtE()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.In.lookup_name)
def _(attrs: list[str], value: Any, state: State) -> ast.Compare:
    """Q(foo__in=[1, 2]) -> self.foo in [1, 2]"""
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.In()],
        comparators=[expression_to_ast(value, state)],
    )


@lookup_to_ast.register(lookup=lookups.Contains.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Compare:
    """Q(foo__contains="bar") -> "bar" in self.foo"""
    return ast.Compare(
        left=expression_to_ast(value, state),
        ops=[ast.In()],
        comparators=[InstanceAttribute(attrs=attrs)],
    )


@lookup_to_ast.register(lookup=lookups.IContains.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Compare:
    """Q(foo__icontains="bar") -> "bar".casefold() in self.foo.casefold()"""
    return ast.Compare(
        left=ast.Call(
            func=ast.Attribute(
                value=expression_to_ast(value, state),
                attr="casefold",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        ),
        ops=[ast.In()],
        comparators=[
            ast.Call(
                func=ast.Attribute(
                    value=InstanceAttribute(attrs=attrs),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        ],
    )


@lookup_to_ast.register(lookup=lookups.StartsWith.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Call:
    """Q(foo__startswith="bar") -> self.foo.startswith("bar")"""
    return ast.Call(
        func=ast.Attribute(
            value=InstanceAttribute(attrs=attrs),
            attr="startswith",
            ctx=ast.Load(),
        ),
        args=[expression_to_ast(value, state)],
        keywords=[],
    )


@lookup_to_ast.register(lookup=lookups.IStartsWith.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Call:
    """Q(foo__istartswith="bar") -> self.foo.casefold().startswith("bar".casefold())"""
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=InstanceAttribute(attrs=attrs),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
            attr="startswith",
            ctx=ast.Load(),
        ),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=expression_to_ast(value, state),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        ],
        keywords=[],
    )


@lookup_to_ast.register(lookup=lookups.EndsWith.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Call:
    """Q(foo__endswith="bar") -> self.foo.endswith("bar")"""
    return ast.Call(
        func=ast.Attribute(
            value=InstanceAttribute(attrs=attrs),
            attr="endswith",
            ctx=ast.Load(),
        ),
        args=[expression_to_ast(value, state)],
        keywords=[],
    )


@lookup_to_ast.register(lookup=lookups.IEndsWith.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Call:
    """Q(foo__iendswith="bar") -> self.foo.casefold().endswith("bar".casefold())"""
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=InstanceAttribute(attrs=attrs),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
            attr="endswith",
            ctx=ast.Load(),
        ),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=expression_to_ast(value, state),
                    attr="casefold",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        ],
        keywords=[],
    )


@lookup_to_ast.register(lookup=lookups.Range.lookup_name)
def _(attrs: list[str], value: tuple[Any, Any], state: State) -> ast.Compare:
    """Q(foo__range=(1, 10)) -> 1 < self.foo < 10"""
    return ast.Compare(
        left=expression_to_ast(value[0], state),
        ops=[ast.Lt(), ast.Lt()],
        comparators=[
            InstanceAttribute(attrs=attrs),
            expression_to_ast(value[1], state),
        ],
    )


@lookup_to_ast.register(lookup=lookups.IsNull.lookup_name)
def _(attrs: list[str], value: bool, state: State) -> ast.Compare:  # noqa: FBT001
    """
    Q(foo__isnull=True) -> self.foo is None
    Q(foo__isnull=False) -> self.foo is not None
    """
    return ast.Compare(
        left=InstanceAttribute(attrs=attrs),
        ops=[ast.Is() if value is True else ast.IsNot()],
        comparators=[expression_to_ast(None, state)],
    )


@lookup_to_ast.register(lookup=lookups.Regex.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Compare:
    """Q(foo__regex=r".*") -> re.match(r".*", self.foo) is not None"""
    state.imports.add("re")
    return ast.Compare(
        left=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="re", ctx=ast.Load()),
                attr="match",
                ctx=ast.Load(),
            ),
            args=[
                expression_to_ast(value, state),
                InstanceAttribute(attrs=attrs),
            ],
            keywords=[],
        ),
        ops=[ast.IsNot()],
        comparators=[expression_to_ast(None, state)],
    )


@lookup_to_ast.register(lookup=lookups.IRegex.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Compare:
    """Q(foo__iregex=r".*") -> re.match(r".*", self.foo.casefold()) is not None"""
    state.imports.add("re")
    return ast.Compare(
        left=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="re", ctx=ast.Load()),
                attr="match",
                ctx=ast.Load(),
            ),
            args=[
                expression_to_ast(value, state),
                ast.Call(
                    func=ast.Attribute(
                        value=InstanceAttribute(attrs=attrs),
                        attr="casefold",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            ],
            keywords=[],
        ),
        ops=[ast.IsNot()],
        comparators=[expression_to_ast(None, state)],
    )
