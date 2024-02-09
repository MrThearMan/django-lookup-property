import pytest
from django.db import models
from django.db.models.functions import Lower, Upper

from lookup_property.field import L
from tests.example.models import Example, Far, Other, Part, Thing, Total
from tests.factories import ExampleFactory, OtherFactory, PartFactory, ThingFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_filter_by_lookup_property():
    ExampleFactory.create()
    assert Example.objects.filter(full_name="foo bar").count() == 1
    assert Example.objects.filter(full_name="fizz buzz").count() == 0
    assert Example.objects.filter(L(full_name="foo bar")).count() == 1


def test_filter_by_related_lookup_property__f():
    ThingFactory.create()
    assert Thing.objects.filter(example__full_name="foo bar").count() == 1
    assert Thing.objects.filter(example__full_name="fizz buzz").count() == 0
    assert Thing.objects.filter(L(example__full_name="foo bar")).count() == 1


def test_filter_by_related_lookup_property__q():
    ThingFactory.create()
    assert Thing.objects.filter(example__q=True).count() == 1
    assert Thing.objects.filter(example__q=False).count() == 0
    assert Thing.objects.filter(L(example__q=True)).count() == 1


def test_filter_by_related_lookup_property__case():
    ThingFactory.create()
    assert Thing.objects.filter(example__case="foo").count() == 1
    assert Thing.objects.filter(example__case="bar").count() == 0
    assert Thing.objects.filter(L(example__case="foo")).count() == 1


def test_filter_by_lookup_property__only():
    ExampleFactory.create()
    assert Example.objects.filter(full_name="foo bar").only("first_name").count() == 1
    assert Example.objects.filter(full_name="fizz buzz").only("last_name").count() == 0
    assert Example.objects.filter(L(full_name="foo bar")).only("first_name").count() == 1


def test_filter_by_lookup_property__with_lookup_expression():
    ExampleFactory.create()
    assert Example.objects.filter(full_name__contains="foo").count() == 1
    assert Example.objects.filter(full_name__contains="fizz").count() == 0
    assert Example.objects.filter(L(full_name__contains="foo")).count() == 1


def test_filter_by_lookup_property__with_transform_expression():
    ExampleFactory.create()
    assert Example.objects.filter(full_name=Upper("full_name")).count() == 0
    assert Example.objects.filter(full_name=Lower("full_name")).count() == 1
    assert Example.objects.filter(L(full_name=Upper("full_name"))).count() == 0


def test_filter_by_lookup_property__subquery():
    other = OtherFactory.create()
    ExampleFactory.create(first_name="a", last_name="a", other=other)
    ExampleFactory.create(first_name="b", last_name="b", other=other)

    subquery = Example.objects.filter(full_name="a a").values("pk")
    assert Other.objects.filter(examples__in=models.Subquery(subquery)).count() == 1

    subquery = Example.objects.filter(L(full_name="a a")).values("pk")
    assert Other.objects.filter(examples__in=models.Subquery(subquery)).count() == 1


def test_filter_by_lookup_property__subquery__outer_ref():
    example_1 = ExampleFactory.create(first_name="a", last_name="a")
    example_2 = ExampleFactory.create(first_name="b", last_name="b")
    PartFactory.create(name="a a", examples=[example_1, example_2])

    subquery = Part.objects.filter(name=models.OuterRef("full_name")).values("pk")
    assert Example.objects.filter(parts__in=models.Subquery(subquery)).count() == 1


def test_filter_by_lookup_property__subquery__outer_ref__case():
    example_1 = ExampleFactory.create()
    example_2 = ExampleFactory.create()
    PartFactory.create(name="foo", examples=[example_1, example_2], far__number=1)

    subquery = Part.objects.filter(name=models.OuterRef("case_6")).values("pk")
    assert Example.objects.filter(parts__in=L(models.Subquery(subquery))).count() == 2


def test_filter_by_lookup_property__subquery__exists():
    other = OtherFactory.create()
    ExampleFactory.create(first_name="a", last_name="a", other=other)
    ExampleFactory.create(first_name="b", last_name="b", other=other)

    subquery_1 = models.Exists(Example.objects.filter(full_name="a a").values("pk"))
    subquery_2 = models.Exists(Example.objects.filter(full_name="c c").values("pk"))
    other = Other.objects.annotate(has_a=subquery_1, has_c=subquery_2).first()
    assert other.has_a is True
    assert other.has_c is False


def test_filter_by_lookup_property__count():
    ExampleFactory.create(parts__aliens__number=1)
    assert Example.objects.filter(count_rel_deep=1).count() == 1
    assert Example.objects.filter(count_rel_deep=0).count() == 0
    assert Example.objects.filter(L(count_rel_deep=1)).count() == 1


def test_filter_by_lookup_property__case_6():
    example = ExampleFactory.create(parts__far__number=1)

    assert Example.objects.count() == 1

    # You can do this, but the below is cleaner.
    assert Example.objects.alias(case_6_alias=Example.case_6.expression).filter(case_6_alias="foo").first() == example

    assert Example.objects.filter(L(case_6="foo")).first() == example
    assert Example.objects.filter(L(case_6="bar")).first() is None


def test_filter_by_lookup_property__case_6__through_related_object__foreign_key():
    example = ExampleFactory.create(parts__far__number=1)
    assert Example.objects.count() == 1

    total = Total.objects.first()
    assert total.example == example

    assert Total.objects.filter(L(example__case_6="foo")).first() == total
    assert Total.objects.filter(L(example__case_6="bar")).first() is None


def test_filter_by_lookup_property__case_6__through_related_object__many_to_many():
    example = ExampleFactory.create(parts__far__number=1)
    assert Example.objects.count() == 1

    part = Part.objects.first()
    assert part.examples.first() == example

    assert Part.objects.filter(L(examples__case_6="foo")).first() == part
    assert Part.objects.filter(L(examples__case_6="bar")).first() is None


def test_filter_by_lookup_property__case_6__through_related_object__two_relations():
    example = ExampleFactory.create(parts__far__number=1)
    assert Example.objects.count() == 1

    far = Far.objects.first()
    assert far.parts.first().examples.first() == example

    assert Far.objects.filter(L(parts__examples__case_6="foo")).first() == far
    assert Far.objects.filter(L(parts__examples__case_6="bar")).first() is None


def test_filter_by_lookup_property__case_6__with_lookups():
    ExampleFactory.create(parts__far__number=1)
    assert Example.objects.filter(L(case_6__contains="foo")).count() == 1
    assert Example.objects.filter(L(case_6__contains="bar")).count() == 0


def test_filter_by_lookup_property__case_6__values():
    ExampleFactory.create(parts__far__number=1)
    # Not ideal, but must use an alias to avoid a collision with the `case_6` model field.
    assert list(Example.objects.values(case_6_alias=L("case_6"))) == [{"case_6_alias": "foo"}]


def test_filter_by_lookup_property__case_6__values_list():
    ExampleFactory.create(parts__far__number=1)
    assert list(Example.objects.values_list(L("case_6"))) == [("foo",)]


def test_filter_by_lookup_property__case_6__values_list_flat():
    ExampleFactory.create(parts__far__number=1)
    assert list(Example.objects.values_list(L("case_6"), flat=True)) == ["foo"]


def test_filter_by_lookup_property__case_7():
    ExampleFactory.create(parts__number=1, parts__far__number=1)
    assert Example.objects.count() == 1

    assert Example.objects.filter(L(case_7="foo")).count() == 1
    assert Example.objects.filter(L(case_7="bar")).count() == 0
