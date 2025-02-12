from django.db.models import F, Q
from django.db.models.expressions import CombinedExpression, NegatedExpression
from django.db.models.functions import Upper

from lookup_property import L
from lookup_property.expressions import extend_expression_to_joined_table
from lookup_property.typing import random_arg_name
from tests.example.models import Example


def test_lookup_property__repr():
    assert (
        repr(Example.full_name)
        == "lookup_property(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), F(last_name)))))"
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


def test_random_arg_name():
    assert len(random_arg_name()) == 20
    assert random_arg_name() != random_arg_name()


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
