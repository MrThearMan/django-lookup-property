import pytest

from example_project.example.models import Example
from lookup_property.typing import Sentinel
from tests.factories import AnotherConcreteFactory, ConcreteFactory, ExampleFactory, ThingFactory

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
    assert example.full_name == "foo bar"
    # This is allowed, but discouraged.
    example.full_name = "fizz"
    assert example.full_name == "fizz"
    # This is a workaround to reset annotations
    example.full_name = Sentinel
    assert example.full_name == "foo bar"


def test_lookup_property__related_property():
    thing = ThingFactory.create()
    assert thing.example.full_name == "foo bar"


def test_lookup_property__only():
    ExampleFactory.create()
    example = Example.objects.only("first_name").first()
    assert example.full_name == "foo bar"


def test_lookup_property__defer():
    ExampleFactory.create()
    example = Example.objects.defer("first_name").first()
    assert example.full_name == "foo bar"


def test_lookup_property__abstract_and_concrete_models():
    concrete = ConcreteFactory.create()
    assert concrete.abstract_property == "abstract property"
    assert concrete.concrete_field == "concrete property"


def test_lookup_property__abstract_and_concrete_models__deep():
    concrete = AnotherConcreteFactory.create()
    assert concrete.abstract_property == "abstract property"
    assert concrete.another_abstract_property == "another abstract property"
    assert concrete.another_concrete_field == "another concrete property"


def test_lookup_property__refs_another_lookup():
    example = ExampleFactory.create(parts__far__number=1)
    assert example.refs_another_lookup == "foo"
