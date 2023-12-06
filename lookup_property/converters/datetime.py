import ast

from django.db.models import functions
from django.db.models.functions.datetime import TruncBase

from ..typing import State
from .expressions import expression_to_ast
from .utils import ast_attribute, ast_function

_LOOKUP_NAME_TO_TRUNC: dict[str, type[TruncBase]] = {
    "year": functions.TruncYear,
    "quarter": functions.TruncQuarter,
    "month": functions.TruncMonth,
    "week": functions.TruncWeek,
    "day": functions.TruncDay,
    "date": functions.TruncDate,
    "time": functions.TruncTime,
    "hour": functions.TruncHour,
    "minute": functions.TruncMinute,
    "second": functions.TruncSecond,
}
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
def _(expression: functions.Now, state: State) -> ast.Call:
    """
    Now() -> datetime.datetime.now()
    Now() -> datetime.datetime.now(tz=datetime.timezone.utc) (if `settings.USE_TZ=True`)
    """
    state.imports.add("datetime")
    kwargs: dict[str, ast.Attribute] = {}

    if state.use_tz:
        kwargs["tz"] = ast_attribute("datetime", "timezone", "utc")

    return ast_function("now", ["datetime", "datetime"], **kwargs)


@expression_to_ast.register
def _(expression: functions.Trunc, state: State) -> ast.AST:
    trunc = _LOOKUP_NAME_TO_TRUNC.get(expression.kind)
    if trunc is None:
        msg = f"No implementation for trunc expression '{expression.kind}'."
        raise ValueError(msg)

    return expression_to_ast(trunc(expression.lhs), state=state)


@expression_to_ast.register
def _(expression: functions.Extract, state: State) -> ast.AST:
    extract = _LOOKUP_NAME_TO_EXTRACT.get(expression.lookup_name)
    if extract is None:
        msg = f"No implementation for extract expression '{expression.lookup_name}'."
        raise ValueError(msg)
    return expression_to_ast(extract(expression.lhs), state=state)


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
