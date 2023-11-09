import pytest

from tests.factories import ExampleFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__q():
    example = ExampleFactory.create()
    assert example.q is True


def test_lookup_property__q_neg():
    example = ExampleFactory.create()
    assert example.q_neg is False


def test_lookup_property__q_empty():
    example = ExampleFactory.create()
    assert example.q_empty is True


def test_lookup_property__q_exact():
    example = ExampleFactory.create()
    assert example.q_exact is True


def test_lookup_property__q_iexact():
    example = ExampleFactory.create()
    assert example.q_iexact_null is False


def test_lookup_property__q_gte():
    example = ExampleFactory.create()
    assert example.q_gte is False


def test_lookup_property__q_gt():
    example = ExampleFactory.create()
    assert example.q_gt is True


def test_lookup_property__q_lte():
    example = ExampleFactory.create()
    assert example.q_lte is True


def test_lookup_property__q_lt():
    example = ExampleFactory.create()
    assert example.q_lt is False


def test_lookup_property__q_in_list():
    example = ExampleFactory.create()
    assert example.q_in_list is True


def test_lookup_property__q_in_tuple():
    example = ExampleFactory.create()
    assert example.q_in_tuple is True


def test_lookup_property__q_in_set():
    example = ExampleFactory.create()
    assert example.q_in_set is True


def test_lookup_property__q_in_dict():
    example = ExampleFactory.create()
    assert example.q_in_dict is True


def test_lookup_property__q_contains():
    example = ExampleFactory.create()
    assert example.q_contains is True


def test_lookup_property__q_icontains():
    example = ExampleFactory.create()
    assert example.q_icontains is True


def test_lookup_property__q_startswith():
    example = ExampleFactory.create()
    assert example.q_startswith is True


def test_lookup_property__q_istartswith():
    example = ExampleFactory.create()
    assert example.q_istartswith is True


def test_lookup_property__q_endswith():
    example = ExampleFactory.create()
    assert example.q_endswith is False


def test_lookup_property__q_iendswith():
    example = ExampleFactory.create()
    assert example.q_iendswith is False


def test_lookup_property__q_range():
    example = ExampleFactory.create()
    assert example.q_range is False


def test_lookup_property__q_isnull():
    example = ExampleFactory.create()
    assert example.q_isnull is False


def test_lookup_property__q_regex():
    example = ExampleFactory.create()
    assert example.q_regex is True


def test_lookup_property__q_iregex():
    example = ExampleFactory.create()
    assert example.q_iregex is True


def test_lookup_property__q_or():
    example = ExampleFactory.create()
    assert example.q_or is True


def test_lookup_property__q_and():
    example = ExampleFactory.create()
    assert example.q_and is True


def test_lookup_property__q_xor():
    example = ExampleFactory.create()
    assert example.q_xor is False
