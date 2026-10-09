import re

import pytest
from django.db.models import F, Q
from django.db.models.expressions import CombinedExpression, NegatedExpression
from django.db.models.functions import Trunc, Upper

from example_project.example.models import Example
from lookup_property import L, lookup_property
from lookup_property.expressions import extend_expression_to_joined_table
from tests.plugins import random_arg_name_patch


def test_lookup_property__repr():
    assert (
        repr(Example.full_name)
        == "LookupPropertyDescriptor(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), F(last_name)))))"
    )


def test_lookup_property__field_repr():
    assert repr(Example.full_name.field) == (
        "LookupPropertyField(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), F(last_name)))))"
    )


def test_lookup_property__col_repr():
    assert repr(Example.full_name.field.cached_col) == (
        "LookupPropertyCol(LookupPropertyField(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), "
        "F(last_name))))))"
    )


def test_lookup_property__name():
    assert Example.full_name.__name__ == "full_name"


def test_l__unpack():
    l_ref = L(foo="bar")
    lookup, value = l_ref
    assert lookup == "foo"
    assert value == "bar"


def test_l__iter():
    it = iter(L(foo="bar"))
    assert next(it) == "foo"
    assert next(it) == "bar"

    it = iter(L("bar"))
    assert next(it) == "bar"


def test_l__index():
    l_ref = L(foo="bar")
    assert l_ref[0] == "foo"
    assert l_ref[1] == "bar"


def test_l__str():
    l_ref = L(foo="bar")
    assert str(l_ref) == "L(foo='bar')"
    l_ref = L("bar")
    assert str(l_ref) == "L('bar')"


def test_l__repr():
    l_ref = L(foo="bar")
    assert repr(l_ref) == "L(foo='bar')"
    l_ref = L("bar")
    assert repr(l_ref) == "L('bar')"


def test_l__len():
    l_ref = L(foo="bar")
    assert len(l_ref) == 2


def test_l__bool():
    l_ref = L(foo="bar")
    assert bool(l_ref) is True


def test_l__contains():
    l_ref = L(foo="bar")
    assert ("foo" in l_ref) is True
    assert ("bar" in l_ref) is True


def test_l__or():
    result = L(foo="bar") | L(fizz="buzz")
    assert result == Q(L(foo="bar")) | Q(L(fizz="buzz"))


def test_l__and():
    result = L(foo="bar") & L(fizz="buzz")
    assert result == Q(L(foo="bar")) & Q(L(fizz="buzz"))


def test_l__xor():
    result = L(foo="bar") ^ L(fizz="buzz")
    assert result == Q(L(foo="bar")) ^ Q(L(fizz="buzz"))


def test_l__or__with_q():
    result = Q(foo="bar") | L(fizz="buzz")
    assert result == Q(foo="bar") | Q(L(fizz="buzz"))


def test_l__or__with_q__reverse():
    result = L(foo="bar") | Q(fizz="buzz")
    assert result == Q(L(foo="bar")) | Q(Q(fizz="buzz"))


def test_l__invert__conditional():
    result = ~L(foo="bar")
    assert result == ~Q(L(foo="bar"))


def test_l__invert__non_conditional():
    result = ~L("bar")
    assert result == NegatedExpression(L("bar"))


def test_l__eq():
    assert L("foo") == L("foo")
    assert L("foo") != L("bar")
    assert L("foo") != "foo"
    assert L("foo") != "foo"


def test_l__combinable():
    assert L("foo") + L("foo") == CombinedExpression(L("foo"), "+", L("foo"))
    assert L("foo") - L("foo") == CombinedExpression(L("foo"), "-", L("foo"))
    assert L("foo") * L("foo") == CombinedExpression(L("foo"), "*", L("foo"))
    assert L("foo") / L("foo") == CombinedExpression(L("foo"), "/", L("foo"))
    assert L("foo") ** L("foo") == CombinedExpression(L("foo"), "^", L("foo"))
    assert L("foo") % L("foo") == CombinedExpression(L("foo"), "%%", L("foo"))


def test_l__hashable():
    assert hash(L("foo"))
    assert hash(L(foo=1))
    assert hash(L(foo=[1]))
    assert hash(L(foo={"bar": 1}))


def test_extend_expression_to_joined_table():
    q1 = Q(foo="bar")
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [("example__foo", "bar")]


def test_extend_expression_to_joined_table__two():
    q1 = Q(foo="bar") & Q(fizz="buzz")
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [("example__foo", "bar"), ("example__fizz", "buzz")]


def test_extend_expression_to_joined_table__two__or():
    q1 = Q(foo="bar") | Q(fizz="buzz")
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [("example__foo", "bar"), ("example__fizz", "buzz")]


def test_extend_expression_to_joined_table__three():
    q1 = Q(foo="bar") & Q(fizz="buzz") & Q(one="two")
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [("example__foo", "bar"), ("example__fizz", "buzz"), ("example__one", "two")]


def test_extend_expression_to_joined_table__child_is_another_q():
    q1 = Q(foo="bar") & (Q(fizz="buzz") | Q(one="two"))
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [("example__foo", "bar"), Q(example__fizz="buzz") | Q(example__one="two")]


def test_extend_expression_to_joined_table__contains_l_ref():
    q1 = Q(L(foo="bar"))
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [L(example__foo="bar")]


def test_extend_expression_to_joined_table__value_is_f_ref():
    q1 = Q(L(foo=F("bar")))
    q2 = extend_expression_to_joined_table(q1, "example")

    assert q2.children == [L(example__foo=F("example__bar"))]


def test_extend_expression_to_joined_table__value_is_func():
    q1 = Q(L(foo=Upper("bar")))
    q2 = extend_expression_to_joined_table(q1, "example")

    assert str(q2.children) == "[L(example__foo=Upper(F(example__bar)))]"


def test_extend_expression_to_joined_table__l_ref():
    l2 = extend_expression_to_joined_table(L("foo"), "example")

    assert l2 == L("example__foo")


def test_lookup_property__col_alias():
    assert Example.full_name.field.cached_col.alias == Example._meta.db_table


def test_lookup_property__col_get_transform():
    assert Example.full_name.field.cached_col.get_transform("foo") is None


def test_lookup_property__col_convert_value__no_output_field():
    col = Example.f_ref.field.cached_col
    assert col.convert_value == col._convert_value_noop


def test_l__positional_and_keyword_argument():
    msg = re.escape("Either one positional or keyword argument can be given.")
    with pytest.raises(ValueError, match=msg):
        L("foo", bar="baz")


def test_l__multiple_keyword_arguments():
    msg = re.escape("Multiple keyword arguments are not supported.")
    with pytest.raises(ValueError, match=msg):
        L(foo="bar", fizz="buzz")


def test_l__no_arguments():
    msg = re.escape("Either one positional or keyword argument must be given.")
    with pytest.raises(ValueError, match=msg):
        L()


def test_lookup_property__skip_codegen__deprecated():
    with pytest.deprecated_call(match="The `skip_codegen` argument is deprecated"):

        @lookup_property(skip_codegen=True)
        def foo() -> str:
            return F("first_name")  # type: ignore[return-value]


def test_lookup_property__override__skips_codegen():
    # Code generation would fail for this expression.
    def foo() -> str:
        return Trunc("unknown", "foo")  # type: ignore[return-value]

    descriptor = lookup_property(foo)

    @descriptor.override
    def _(self: Example) -> str:
        return "override"

    descriptor.contribute_to_class(Example, "foo")

    assert descriptor.func(Example()) == "override"


def test_random_arg_name():
    # The test plugin replaces 'random_arg_name' for the whole test run, so call the original.
    name = random_arg_name_patch.temp_original()

    assert re.fullmatch(r"[a-z]{20}", name)
