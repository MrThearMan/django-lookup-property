import pytest

from tests.example.models import Example
from tests.factories import ExampleFactory, ThingFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__simple():
    example = ExampleFactory.create()
    assert example.full_name == "foo bar"


def test_lookup_property__to_another_lookup_property():
    example = ExampleFactory.create()
    assert example.name == "foo bar"


def test_lookup_property__refresh_from_db():
    example = ExampleFactory.create()
    assert example.full_name == "foo bar"
    Example.objects.update(first_name="fizz", last_name="buzz")
    assert example.full_name == "foo bar"
    example.refresh_from_db()
    assert example.full_name == "fizz buzz"


def test_lookup_property__set_attribute():
    example = ExampleFactory.create()
    example.full_name = "fizz"
    assert example.full_name == "foo bar"


def test_lookup_property__related_property():
    thing = ThingFactory.create()
    assert thing.example.full_name == "foo bar"
