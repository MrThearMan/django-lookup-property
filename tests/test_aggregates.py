import pytest

from tests.factories import AlienFactory, ExampleFactory, PartFactory, TotalFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__count_field():
    example = ExampleFactory.create()
    assert example.count_field == 1
    ExampleFactory.create()
    assert example.count_field == 2


def test_lookup_property__count_field_filter():
    example = ExampleFactory.create(number=11)
    assert example.count_field_filter == 0
    ExampleFactory.create(number=9)
    assert example.count_field_filter == 1


def test_lookup_property__count_rel():
    example = ExampleFactory.create()
    assert example.count_rel == 0
    TotalFactory.create(example=example)
    assert example.count_rel == 1


def test_lookup_property__count_rel_many_to_many():
    example = ExampleFactory.create()
    assert example.count_rel_many_to_many == 0
    alien = AlienFactory.create()
    part = PartFactory.create()
    part.examples.add(example)
    alien.parts.add(part)
    assert example.count_rel_many_to_many == 1


def test_lookup_property__count_rel_filter():
    example = ExampleFactory.create()
    assert example.count_rel_filter == 0
    TotalFactory.create(name="foo", example=example)
    assert example.count_rel_filter == 0
    TotalFactory.create(name="bar", example=example)
    assert example.count_rel_filter == 1


def test_lookup_property__max():
    example = ExampleFactory.create(number=1)
    assert example.max_ == 1
    ExampleFactory.create(number=3)
    assert example.max_ == 3


def test_lookup_property__max_rel():
    example = ExampleFactory.create()
    TotalFactory.create(example=example, number=1)
    assert example.max_rel == 1
    TotalFactory.create(example=example, number=3)
    assert example.max_rel == 3


def test_lookup_property__min():
    example = ExampleFactory.create(number=1)
    assert example.min_ == 1
    ExampleFactory.create(number=3)
    assert example.min_ == 1


def test_lookup_property__min_rel():
    example = ExampleFactory.create()
    TotalFactory.create(example=example, number=1)
    assert example.min_rel == 1
    TotalFactory.create(example=example, number=3)
    assert example.min_rel == 1


def test_lookup_property__sum():
    example = ExampleFactory.create(number=1)
    assert example.sum_ == 1
    ExampleFactory.create(number=3)
    assert example.sum_ == 4


def test_lookup_property__sum_rel():
    example = ExampleFactory.create()
    TotalFactory.create(example=example, number=1)
    assert example.sum_rel == 1
    TotalFactory.create(example=example, number=4)
    assert example.sum_rel == 5


def test_lookup_property__sum_filter():
    example = ExampleFactory.create(number=1)
    assert example.sum_filter == 1
    ExampleFactory.create(number=4)
    assert example.sum_filter == 1


def test_lookup_property__avg():
    example = ExampleFactory.create(number=1)
    assert example.avg == 1.0
    ExampleFactory.create(number=3)
    assert example.avg == 2.0


def test_lookup_property__std_dev():
    example = ExampleFactory.create(number=1)
    assert example.std_dev == 0.0
    ExampleFactory.create(number=3)
    assert example.std_dev == 1.0


def test_lookup_property__variance():
    example = ExampleFactory.create(number=1)
    assert example.variance == 0.0
    ExampleFactory.create(number=3)
    assert example.variance == 1.0
