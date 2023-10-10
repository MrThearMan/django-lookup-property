import pytest

from tests.factories import ExampleFactory, PartFactory, ThingFactory, TotalFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__rel_one_to_one():
    thing = ThingFactory.create()
    assert thing.example.rel_one_to_one == thing.pk


def test_lookup_property__rel_many_to_one():
    example = ExampleFactory.create()
    assert example.rel_many_to_one == example.other.pk


def test_lookup_property__rel_one_to_many():
    total = TotalFactory.create()
    assert total.example.rel_one_to_many == total.pk


def test_lookup_property__rel_many_to_many():
    example = ExampleFactory.create()
    part = PartFactory.create(examples=[example])
    assert example.rel_many_to_many == part.pk
