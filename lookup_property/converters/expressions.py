import ast
import random
import string
from functools import singledispatch

from django.db import models
from django.db.models import functions
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import CombinedExpression
from django.db.models.functions import MD5, SHA1, SHA224, SHA256, SHA384, SHA512, Random  # type: ignore[attr-defined]
from django.db.models.functions.datetime import TruncBase

from ..typing import Any, Expr, InstanceAttribute, State, cast

__all__ = [
    "expression_to_ast",
]


@singledispatch
def expression_to_ast(expression: Any, state: State) -> ast.AST:
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
    arg = random_arg_name()
    state.extra_kwargs[arg] = lambda: expression
    return ast.Call(
        func=ast.Name(id=arg, ctx=ast.Load()),
        args=[],
        keywords=[],
    )


def random_arg_name() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=20))


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
    return ast.Set(
        elts=[expression_to_ast(value, state) for value in expression],
    )


@expression_to_ast.register
def _(expression: tuple, state: State) -> ast.Tuple:
    """Convert to tuples: (..., ..., ...)"""
    return ast.Tuple(
        elts=[expression_to_ast(value, state) for value in expression],
        ctx=ast.Load(),
    )


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
    return InstanceAttribute(attrs=expression.name.split(LOOKUP_SEP))


_SIGN_TO_OP: dict[str, ast.operator] = {
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


@expression_to_ast.register
def _(expression: CombinedExpression, state: State) -> ast.BinOp:
    """
    F("foo") * F("bar") -> self.foo * self.bar
    F("foo") + Value(2) -> self.foo + 2
    """
    left = expression_to_ast(expression.lhs, state)
    right = expression_to_ast(expression.rhs, state)

    op = _SIGN_TO_OP.get(expression.connector)
    if op is None:
        msg = f"No implementation for connector '{expression.connector}'."
        raise ValueError(msg)

    return ast.BinOp(left=left, op=op, right=right)


@expression_to_ast.register
def _(expression: functions.Concat, state: State) -> ast.AST:
    """
    Used together with the ConcatPair-converter below to concatenate values in pairs:
    Concat(F("foo"), Value(" "), F("bar")) -> self.foo + ("" + self.bar)
    """
    source_expressions = expression.get_source_expressions()
    return expression_to_ast(source_expressions[0], state)


@expression_to_ast.register
def _(expression: functions.ConcatPair, state: State) -> ast.BinOp:
    """Concat(F("foo"), F("bar")) -> self.foo + self.bar"""
    source_expressions = expression.get_source_expressions()
    left = expression_to_ast(source_expressions[0], state)
    right = expression_to_ast(source_expressions[1], state)
    return ast.BinOp(left=left, op=ast.Add(), right=right)


@expression_to_ast.register
def _(expression: functions.Now, state: State) -> ast.Call:
    """
    Now() -> datetime.datetime.now()
    Now() -> datetime.datetime.now(tz=datetime.UTC) (if `settings.USE_TZ=True`)
    """
    state.imports.add("datetime")
    keywords: list[ast.keyword] = []
    if state.use_tz:
        keywords.append(
            ast.keyword(
                arg="tz",
                value=ast.Attribute(
                    value=ast.Name(id="datetime", ctx=ast.Load()),
                    attr="UTC",
                    ctx=ast.Load(),
                ),
            ),
        )

    return ast.Call(
        func=ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id="datetime", ctx=ast.Load()),
                attr="datetime",
                ctx=ast.Load(),
            ),
            attr="now",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=keywords,
    )


_KIND_TO_TRUNC: dict[str, type[TruncBase]] = {
    "year": functions.TruncYear,
    "quarter": functions.TruncQuarter,
    "month": functions.TruncMonth,
    "week": functions.TruncWeek,
    "day": functions.TruncDay,
    "date": functions.TruncDate,
    "time": functions.TruncTime,
    "hour": functions.TruncHour,
    "minute": functions.TruncMinute,
    "TruncSecond": functions.TruncSecond,
}


@expression_to_ast.register
def _(expression: functions.Trunc, state: State) -> ast.AST:
    trunc = _KIND_TO_TRUNC.get(expression.kind)
    if trunc is None:
        msg = f"No implementation for trunc expression '{expression.kind}'."
        raise ValueError(msg)
    expr: Expr = expression.lhs
    return expression_to_ast(trunc(expr), state=state)


_LOOKUP_NAME_TO_EXTRACT: dict[str, type[functions.Extract]] = {
    "year": functions.ExtractYear,
    "quarter": functions.ExtractQuarter,
    "month": functions.ExtractMonth,
    "week": functions.ExtractWeek,
    "day": functions.ExtractDay,
    "hour": functions.ExtractHour,
    "minute": functions.ExtractMinute,
    "second": functions.ExtractSecond,
    "iso_year": functions.ExtractIsoYear,
    "week_day": functions.ExtractWeekDay,
    "iso_week_day": functions.ExtractIsoWeekDay,
}


@expression_to_ast.register
def _(expression: functions.Extract, state: State) -> ast.AST:
    extract = _LOOKUP_NAME_TO_EXTRACT.get(expression.lookup_name)
    if extract is None:
        msg = f"No implementation for extract expression '{expression.lookup_name}'."
        raise ValueError(msg)
    expr: Expr = expression.lhs
    return expression_to_ast(extract(expr), state=state)


@expression_to_ast.register
def _(expression: functions.TruncYear | functions.ExtractYear, state: State) -> ast.Attribute:
    """TruncYear("foo") -> self.foo.year"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="year",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncMonth | functions.ExtractMonth, state: State) -> ast.Attribute:
    """TruncMonth("foo") -> self.foo.month"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="month",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncDay | functions.ExtractDay, state: State) -> ast.Attribute:
    """TruncDay("foo") -> self.foo.day"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="day",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncHour | functions.ExtractHour, state: State) -> ast.Attribute:
    """TruncHour("foo") -> self.foo.hour"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="hour",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncMinute | functions.ExtractMinute, state: State) -> ast.Attribute:
    """TruncMinute("foo") -> self.foo.minute"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="minute",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncSecond | functions.ExtractSecond, state: State) -> ast.Attribute:
    """TruncSecond("foo") -> self.foo.second"""
    return ast.Attribute(
        value=expression_to_ast(expression.lhs, state=state),
        attr="second",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.TruncQuarter | functions.ExtractQuarter, state: State) -> ast.Call:
    """
    TruncQuarter("foo")
    -> self.foo.replace(month=(self.foo.month + 2) // 3, day=1, hour=0, minute=0, second=0, microsecond=0)
    """
    state.imports.add("datetime")
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="replace",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[
            ast.keyword(
                arg="month",
                value=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Attribute(
                            value=expression_to_ast(expression.lhs, state=state),
                            attr="month",
                            ctx=ast.Load(),
                        ),
                        op=ast.Add(),
                        right=ast.Constant(value=2),
                    ),
                    op=ast.FloorDiv(),
                    right=ast.Constant(value=3),
                ),
            ),
            ast.keyword(arg="day", value=ast.Constant(value=1)),
            ast.keyword(arg="hour", value=ast.Constant(value=0)),
            ast.keyword(arg="minute", value=ast.Constant(value=0)),
            ast.keyword(arg="second", value=ast.Constant(value=0)),
            ast.keyword(arg="microsecond", value=ast.Constant(value=0)),
        ],
    )


@expression_to_ast.register
def _(expression: functions.TruncWeek, state: State) -> ast.BinOp:
    """
    TruncWeek("foo")
    -> self.foo.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=self.foo.weekday())
    """
    state.imports.add("datetime")
    return ast.BinOp(
        left=ast.Call(
            func=ast.Attribute(
                value=expression_to_ast(expression.lhs, state=state),
                attr="replace",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(arg="hour", value=ast.Constant(value=0)),
                ast.keyword(arg="minute", value=ast.Constant(value=0)),
                ast.keyword(arg="second", value=ast.Constant(value=0)),
                ast.keyword(arg="microsecond", value=ast.Constant(value=0)),
            ],
        ),
        op=ast.Sub(),
        right=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="datetime", ctx=ast.Load()),
                attr="timedelta",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg="days",
                    value=ast.Call(
                        func=ast.Attribute(
                            value=expression_to_ast(expression.lhs, state=state),
                            attr="weekday",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ),
            ],
        ),
    )


@expression_to_ast.register
def _(expression: functions.TruncDate, state: State) -> ast.Call:
    """TruncDate("foo") -> self.foo.date()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="date",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.TruncTime, state: State) -> ast.Call:
    """
    TruncTime("foo") -> self.foo.time()
    TruncTime("foo") -> self.foo.timetz() (if `settings.USE_TZ=True`)
    """
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="timetz" if state.use_tz else "time",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.ExtractIsoYear, state: State) -> ast.Attribute:
    """ExtractIsoYear("foo") -> self.foo.isocalendar().year"""
    return ast.Attribute(
        value=ast.Call(
            func=ast.Attribute(
                value=expression_to_ast(expression.lhs, state=state),
                attr="isocalendar",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        ),
        attr="year",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.ExtractWeek, state: State) -> ast.Attribute:
    """ExtractWeekDay("foo") -> self.foo.isocalendar().week"""
    return ast.Attribute(
        value=ast.Call(
            func=ast.Attribute(
                value=expression_to_ast(expression.lhs, state=state),
                attr="isocalendar",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        ),
        attr="week",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.ExtractIsoWeekDay, state: State) -> ast.Attribute:
    """ExtractIsoWeekDay("foo") -> self.foo.isocalendar().weekday"""
    return ast.Attribute(
        value=ast.Call(
            func=ast.Attribute(
                value=expression_to_ast(expression.lhs, state=state),
                attr="isocalendar",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        ),
        attr="weekday",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.ExtractWeekDay, state: State) -> ast.BinOp:
    """ExtractWeekDay("foo") -> self.foo.isocalendar().weekday - 1"""
    return ast.BinOp(
        left=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=expression_to_ast(expression.lhs, state=state),
                    attr="isocalendar",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
            attr="weekday",
            ctx=ast.Load(),
        ),
        op=ast.Sub(),
        right=ast.Constant(value=1),
    )


@expression_to_ast.register
def _(expression: functions.Upper, state: State) -> ast.Call:
    """Upper("foo") -> self.foo.upper()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="upper",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Lower, state: State) -> ast.Call:
    """Lower("foo") -> self.foo.lower()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="lower",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.LPad, state: State) -> ast.Call:
    """LPad("foo", length=20, fill_text=".") -> self.foo.rjust(20, ".")"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="rjust",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.RPad, state: State) -> ast.Call:
    """RPad("foo", length=20, fill_text=".") -> self.foo.ljust(20, ".")"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="ljust",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.RTrim, state: State) -> ast.Call:
    """RTrim("foo") -> self.foo.rstrip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="rstrip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.LTrim, state: State) -> ast.Call:
    """LTrim("foo") -> self.foo.lstrip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="lstrip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Length, state: State) -> ast.Call:
    """Length("foo") -> len(self.foo)"""
    return ast.Call(
        func=ast.Name(id="len", ctx=ast.Load()),
        args=[expression_to_ast(expression.lhs, state=state)],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Left, state: State) -> ast.Subscript:
    """Left("foo", length=1) -> self.foo[:1]"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=None,
            upper=expression_to_ast(arguments[1], state=state),
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Right, state: State) -> ast.Subscript:
    """Right("foo", length=1) -> self.foo[-1:]"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=ast.UnaryOp(
                op=ast.USub(),
                operand=expression_to_ast(arguments[1], state=state),
            ),
            upper=None,
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Repeat, state: State) -> ast.BinOp:
    """Repeat("foo", length=3) -> self.foo * 3"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.BinOp(
        left=expression_to_ast(arguments[0], state=state),
        op=ast.Mult(),
        right=expression_to_ast(arguments[1], state=state),
    )


@expression_to_ast.register
def _(expression: functions.Replace, state: State) -> ast.Call:
    """Replace("foo", text=Value("oo"), replacement=Value("uu")) -> self.foo.replace('oo', 'uu')"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(arguments[0], state=state),
            attr="replace",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[1], state=state),
            expression_to_ast(arguments[2], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Reverse, state: State) -> ast.Subscript:
    """Reverse("foo") -> self.foo[::-1]"""
    return ast.Subscript(
        value=expression_to_ast(expression.lhs, state=state),
        slice=ast.Slice(
            lower=None,
            upper=None,
            step=ast.UnaryOp(
                op=ast.USub(),
                operand=ast.Constant(value=1),
            ),
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.StrIndex, state: State) -> ast.If:
    """
    StrIndex("foo", Value("o"))

    ->

    if 'o' in self.foo:
        return self.foo.index('o') + 1
    else:
        return 0
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.If(
        test=ast.Compare(
            left=expression_to_ast(arguments[1], state=state),
            ops=[ast.In()],
            comparators=[expression_to_ast(arguments[0], state=state)],
        ),
        body=[
            ast.Return(
                value=ast.BinOp(
                    left=ast.Call(
                        func=ast.Attribute(
                            value=expression_to_ast(arguments[0], state=state),
                            attr="index",
                            ctx=ast.Load(),
                        ),
                        args=[expression_to_ast(arguments[1], state=state)],
                        keywords=[],
                    ),
                    op=ast.Add(),
                    right=ast.Constant(value=1),
                ),
            ),
        ],
        orelse=[
            ast.Return(value=ast.Constant(value=0)),
        ],
    )


@expression_to_ast.register
def _(expression: functions.Substr, state: State) -> ast.Subscript:
    """
    Substr("foo", x) -> self.foo[x - 1:]
    Substr("foo", x, y) -> self.foo[x - 1:x + y - 1]
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Subscript(
        value=expression_to_ast(arguments[0], state=state),
        slice=ast.Slice(
            lower=ast.BinOp(
                left=expression_to_ast(arguments[1], state),
                op=ast.Sub(),
                right=ast.Constant(value=1),
            ),
            upper=(
                ast.BinOp(
                    left=ast.BinOp(
                        left=expression_to_ast(arguments[1], state),
                        op=ast.Add(),
                        right=expression_to_ast(arguments[2], state),
                    ),
                    op=ast.Sub(),
                    right=ast.Constant(value=1),
                )
                if len(arguments) == 3  # noqa: PLR2004
                else None
            ),
            step=None,
        ),
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Trim, state: State) -> ast.Call:
    """Trim("foo") -> self.foo.strip()"""
    return ast.Call(
        func=ast.Attribute(
            value=expression_to_ast(expression.lhs, state=state),
            attr="strip",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


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


@expression_to_ast.register
def _(expression: functions.Ord, state: State) -> ast.Call:
    """Ord("foo") -> ord(self.foo)"""
    return ast.Call(
        func=ast.Name(id="ord", ctx=ast.Load()),
        args=[
            ast.Subscript(
                value=expression_to_ast(expression.lhs, state=state),
                slice=ast.Constant(value=0),
                ctx=ast.Load(),
            ),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: MD5 | SHA1 | SHA224 | SHA256 | SHA384 | SHA512, state: State) -> ast.Call:
    """
    MD5("foo") -> hashlib.md5(self.foo.encode()).hexdigest()
    SHA1("foo") -> hashlib.sha1(self.foo.encode()).hexdigest()
    SHA224("foo") -> hashlib.sha224(self.foo.encode()).hexdigest()
    SHA256("foo") -> hashlib.sha256(self.foo.encode()).hexdigest()
    SHA384("foo") -> hashlib.sha384(self.foo.encode()).hexdigest()
    SHA512("foo") -> hashlib.sha512(self.foo.encode()).hexdigest()
    """
    state.imports.add("hashlib")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="hashlib", ctx=ast.Load()),
                    attr=expression.__class__.__name__.lower(),
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Call(
                        func=ast.Attribute(
                            value=expression_to_ast(expression.lhs, state=state),
                            attr="encode",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ],
                keywords=[],
            ),
            attr="hexdigest",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


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


@expression_to_ast.register
def _(expression: functions.Greatest, state: State) -> ast.Call:
    """Coalesce("foo", "bar") -> max({self.foo, self.bar}.difference({None}), default=None)"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="max", ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Set(elts=[expression_to_ast(arg, state=state) for arg in arguments]),
                    attr="difference",
                    ctx=ast.Load(),
                ),
                args=[ast.Set(elts=[ast.Constant(value=None)])],
                keywords=[],
            ),
        ],
        keywords=[
            ast.keyword(
                arg="default",
                value=ast.Constant(value=None),
            ),
        ],
    )


@expression_to_ast.register
def _(expression: functions.Least, state: State) -> ast.Call:
    """Coalesce("foo", "bar") -> min({self.foo, self.bar}.difference({None}), default=None)"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="min", ctx=ast.Load()),
        args=[
            ast.Call(
                func=ast.Attribute(
                    value=ast.Set(elts=[expression_to_ast(arg, state=state) for arg in arguments]),
                    attr="difference",
                    ctx=ast.Load(),
                ),
                args=[ast.Set(elts=[ast.Constant(value=None)])],
                keywords=[],
            ),
        ],
        keywords=[
            ast.keyword(
                arg="default",
                value=ast.Constant(value=None),
            ),
        ],
    )


@expression_to_ast.register
def _(expression: functions.JSONObject, state: State) -> ast.Dict:
    """JSONObject(foo=1) -> {'foo': 1}"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Dict(
        keys=[expression_to_ast(key, state) for key in arguments[::2]],
        values=[expression_to_ast(key, state) for key in arguments[1::2]],
    )


@expression_to_ast.register
def _(expression: functions.NullIf, state: State) -> ast.IfExp:
    """NullIf("foo", "bar") -> None if self.foo == self.bar else self.foo"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.IfExp(
        test=ast.Compare(
            left=expression_to_ast(arguments[0], state),
            ops=[ast.Eq()],
            comparators=[expression_to_ast(arguments[1], state)],
        ),
        body=ast.Constant(value=None),
        orelse=expression_to_ast(arguments[0], state),
    )


@expression_to_ast.register
def _(expression: functions.Abs, state: State) -> ast.Call:
    """Abs("foo") -> abs(self.foo)"""
    return ast.Call(
        func=ast.Name(id="abs", ctx=ast.Load()),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(
    expression: (
        functions.ACos
        | functions.ASin
        | functions.ATan
        | functions.Ceil
        | functions.Cos
        | functions.Degrees
        | functions.Exp
        | functions.Floor
        | functions.Radians
        | functions.Sin
        | functions.Sqrt
        | functions.Tan
    ),
    state: State,
) -> ast.Call:
    """
    ACos("foo") -> math.acos(self.foo)
    Ceil("foo") -> math.ceil(self.foo)
    etc.
    """
    state.imports.add("math")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr=expression.__class__.__name__.lower(),
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Cot, state: State) -> ast.BinOp:
    """Cot("foo") -> 1 / math.tan(self.foo)"""
    state.imports.add("math")
    return ast.BinOp(
        left=ast.Constant(value=1),
        op=ast.Div(),
        right=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="math", ctx=ast.Load()),
                attr="tan",
                ctx=ast.Load(),
            ),
            args=[
                expression_to_ast(expression.lhs, state=state),
            ],
            keywords=[],
        ),
    )


@expression_to_ast.register
def _(expression: functions.Pi, state: State) -> ast.Attribute:
    """Pi() -> math.pi"""
    state.imports.add("math")
    return ast.Attribute(
        value=ast.Name(id="math", ctx=ast.Load()),
        attr="pi",
        ctx=ast.Load(),
    )


@expression_to_ast.register
def _(expression: functions.Power, state: State) -> ast.Call:
    """Power("foo", 3) -> math.pow(self.foo, 3)"""
    state.imports.add("math")
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr="pow",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[0], state=state),
            expression_to_ast(arguments[1], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.ATan2 | functions.Log, state: State) -> ast.Call:
    """
    ATan2("foo", 3) -> math.atan2(self.foo, 3)
    Log("foo", 10) -> math.log(self.foo, 10)
    """
    state.imports.add("math")
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr=expression.__class__.__name__.lower(),
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(arguments[0], state=state),
            expression_to_ast(arguments[1], state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Ln, state: State) -> ast.Call:
    """Ln("foo") -> math.log(self.foo)  # default base is 'e' (=ln)"""
    state.imports.add("math")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()),
            attr="log",
            ctx=ast.Load(),
        ),
        args=[
            expression_to_ast(expression.lhs, state=state),
        ],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Mod, state: State) -> ast.BinOp:
    """Mod("foo", 4) -> self.foo % 4"""
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.BinOp(
        left=expression_to_ast(arguments[0], state=state),
        op=ast.Mod(),
        right=expression_to_ast(arguments[1], state=state),
    )


@expression_to_ast.register
def _(expression: Random, state: State) -> ast.Call:
    """Random() -> random.random()"""
    state.imports.add("random")
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="random", ctx=ast.Load()),
            attr="random",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Round, state: State) -> ast.Call:
    """
    Round("foo") -> round(self.foo)
    Round("foo", precision=2) -> round(self.foo, 2)
    """
    arguments: list[Expr] = expression.get_source_expressions()
    return ast.Call(
        func=ast.Name(id="round", ctx=ast.Load()),
        args=[expression_to_ast(arg, state=state) for arg in arguments],
        keywords=[],
    )


@expression_to_ast.register
def _(expression: functions.Sign, state: State) -> ast.BinOp:
    """Sign("foo") -> int(self.foo > 0) - int(self.foo < 0)  # -1 or 0 or 1"""
    return ast.BinOp(
        left=ast.Call(
            func=ast.Name(id="int", ctx=ast.Load()),
            args=[
                ast.Compare(
                    left=expression_to_ast(expression.lhs, state=state),
                    ops=[ast.Gt()],
                    comparators=[ast.Constant(value=0)],
                ),
            ],
            keywords=[],
        ),
        op=ast.Sub(),
        right=ast.Call(
            func=ast.Name(id="int", ctx=ast.Load()),
            args=[
                ast.Compare(
                    left=expression_to_ast(expression.lhs, state=state),
                    ops=[ast.Lt()],
                    comparators=[ast.Constant(value=0)],
                ),
            ],
            keywords=[],
        ),
    )
