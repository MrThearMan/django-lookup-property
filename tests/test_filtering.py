import pytest
from django.db import models
from django.db.models.functions import Lower, Upper

from tests.example.models import Example, Other, Part, Thing
from tests.factories import ExampleFactory, OtherFactory, PartFactory, ThingFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_filter_by_lookup_property():
    ExampleFactory.create()
    assert Example.objects.filter(full_name="foo bar").count() == 1
    assert Example.objects.filter(full_name="fizz buzz").count() == 0


def test_filter_by_related_lookup_property__f():
    ThingFactory.create()
    assert Thing.objects.filter(example__full_name="foo bar").count() == 1
    assert Thing.objects.filter(example__full_name="fizz buzz").count() == 0


def test_filter_by_related_lookup_property__q():
    ThingFactory.create()
    assert Thing.objects.filter(example__q=True).count() == 1
    assert Thing.objects.filter(example__q=False).count() == 0


def test_filter_by_related_lookup_property__case():
    ThingFactory.create()
    assert Thing.objects.filter(example__case=1).count() == 1
    assert Thing.objects.filter(example__case=2).count() == 0


def test_filter_by_lookup_property__only():
    ExampleFactory.create()
    assert Example.objects.filter(full_name="foo bar").only("first_name").count() == 1
    assert Example.objects.filter(full_name="fizz buzz").only("last_name").count() == 0


def test_filter_by_lookup_property__with_lookup_expression():
    ExampleFactory.create()
    assert Example.objects.filter(full_name__contains="foo").count() == 1
    assert Example.objects.filter(full_name__contains="fizz").count() == 0


def test_filter_by_lookup_property__with_transform_expression():
    ExampleFactory.create()
    assert Example.objects.filter(full_name=Upper("full_name")).count() == 0
    assert Example.objects.filter(full_name=Lower("full_name")).count() == 1


def test_filter_by_lookup_property__subquery():
    other = OtherFactory.create()
    ExampleFactory.create(first_name="a", last_name="a", other=other)
    ExampleFactory.create(first_name="b", last_name="b", other=other)

    subquery = Example.objects.filter(full_name="a a").values("pk")
    assert Other.objects.filter(examples__in=models.Subquery(subquery)).count() == 1


def test_filter_by_lookup_property__subquery__outer_ref():
    example_1 = ExampleFactory.create(first_name="a", last_name="a")
    example_2 = ExampleFactory.create(first_name="b", last_name="b")
    PartFactory.create(name="a a", examples=[example_1, example_2])

    subquery = Part.objects.filter(name=models.OuterRef("full_name")).values("pk")
    assert Example.objects.filter(parts__in=models.Subquery(subquery)).count() == 1


def test_filter_by_lookup_property__subquery__exists():
    other = OtherFactory.create()
    ExampleFactory.create(first_name="a", last_name="a", other=other)
    ExampleFactory.create(first_name="b", last_name="b", other=other)

    subquery_1 = models.Exists(Example.objects.filter(full_name="a a").values("pk"))
    subquery_2 = models.Exists(Example.objects.filter(full_name="c c").values("pk"))
    other = Other.objects.annotate(has_a=subquery_1, has_c=subquery_2).first()
    assert other.has_a is True
    assert other.has_c is False
