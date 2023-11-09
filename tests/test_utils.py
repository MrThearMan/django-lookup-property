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
