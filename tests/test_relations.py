import pytest

from tests.example.models import Example
from tests.factories import (
    ChildFactory,
    ExampleFactory,
    OtherFactory,
    PartFactory,
    ThingFactory,
    TotalFactory,
)

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__one_to_one():
    thing = ThingFactory.create()
    assert thing.example.reverse_one_to_one == thing.pk


def test_lookup_property__many_to_one():
    example = ExampleFactory.create()
    assert example.forward_many_to_one == example.other.pk


def test_lookup_property__one_to_many():
    total = TotalFactory.create()
    assert total.example.reverse_one_to_many == total.pk


def test_lookup_property__many_to_many():
    example = ExampleFactory.create()
    part = PartFactory.create(examples=[example])
    assert example.reverse_many_to_many == part.pk


def test_lookup_property__double_join():
    thing = ThingFactory.create()
    assert thing.example.double_join == thing.far.pk


def test_filter_by_lookup__one_to_one__forward():
    example = ExampleFactory.create()
    assert Example.objects.filter(forward_one_to_one=example.question.pk).count() == 1


def test_filter_by_lookup__one_to_one__reverse():
    example = ExampleFactory.create()
    thing = ThingFactory.create(example=example)
    assert Example.objects.filter(reverse_one_to_one=thing.pk).first() == example


def test_filter_by_lookup__one_to_one__reverse__count():
    example = ExampleFactory.create()
    thing = ThingFactory.create(example=example)
    assert Example.objects.filter(reverse_one_to_one=thing.pk).count() == 1


def test_filter_by_lookup__many_to_one__forward():
    other = OtherFactory.create()
    example = ExampleFactory.create(other=other)
    assert Example.objects.filter(forward_many_to_one=other.pk).first() == example


def test_filter_by_lookup__one_to_many__reverse():
    example = ExampleFactory.create()
    total = TotalFactory.create(example=example)
    assert Example.objects.filter(reverse_one_to_many=total.pk).first() == example


def test_filter_by_lookup__one_to_many__reverse__count():
    example = ExampleFactory.create()
    total = TotalFactory.create(example=example)
    assert Example.objects.filter(reverse_one_to_many=total.pk).count() == 1


def test_filter_by_lookup__many_to_many__forward():
    example = ExampleFactory.create()
    child = ChildFactory.create()
    example.children.add(child)
    assert Example.objects.filter(forward_many_to_many=child.pk).first() == example


def test_filter_by_lookup__many_to_many__forward__count():
    example = ExampleFactory.create()
    child = ChildFactory.create()
    example.children.add(child)
    assert Example.objects.filter(forward_many_to_many=child.pk).count() == 1


def test_filter_by_lookup__many_to_many__reverse():
    example = ExampleFactory.create()
    part = PartFactory.create()
    part.examples.add(example)
    assert Example.objects.filter(reverse_many_to_many=part.pk).first() == example


def test_filter_by_lookup__many_to_many__reverse__count():
    example = ExampleFactory.create()
    part = PartFactory.create()
    part.examples.add(example)
    assert Example.objects.filter(reverse_many_to_many=part.pk).count() == 1


def test_filter_by_lookup__double_join():
    example = ExampleFactory.create()
    thing = ThingFactory.create(example=example)
    assert Example.objects.filter(double_join=thing.far.pk).first() == example
