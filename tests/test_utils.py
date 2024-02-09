from lookup_property import L
from lookup_property.typing import random_arg_name
from tests.example.models import Example


def test_lookup_property_repr():
    assert (
        repr(Example.full_name)
        == "lookup_property(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), F(last_name)))))"
    )


def test_lookup_property_field_repr():
    assert repr(Example.full_name.field) == (
        "LookupPropertyField(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), " "F(last_name)))))"
    )


def test_lookup_property_col_repr():
    assert repr(Example.full_name.field.cached_col) == (
        "LookupPropertyCol(LookupPropertyField(Concat(ConcatPair(F(first_name), ConcatPair(Value(' '), "
        "F(last_name))))))"
    )


def test_random_arg_name():
    assert len(random_arg_name()) == 20
    assert random_arg_name() != random_arg_name()


def test_l__unpack():
    l_ref = L(foo="bar")
    lookup, value = l_ref
    assert lookup == "foo"
    assert value == "bar"


def test_l__index():
    l_ref = L(foo="bar")
    assert l_ref[0] == "foo"
    assert l_ref[1] == "bar"


def test_l__str():
    l_ref = L(foo="bar")
    assert str(l_ref) == "L(foo='bar')"


def test_l__repr():
    l_ref = L(foo="bar")
    assert repr(l_ref) == "L(foo='bar')"


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
