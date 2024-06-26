import pytest
from django.db import models
from django.db.models.functions import Lower, Upper

from lookup_property import L
from tests.example.models import Example, Far, Other, Part, Thing, Total
from tests.factories import (
    AlienFactory,
    ExampleFactory,
    FarFactory,
    OtherFactory,
    PartFactory,
    ThingFactory,
    TotalFactory,
)

pytestmark = [
    pytest.mark.django_db,
]


def test_filter_by_lookup_property():
    ExampleFactory.create()
    assert Example.objects.filter(_full_name="foo bar").count() == 1
    assert Example.objects.filter(_full_name="fizz buzz").count() == 0
    assert Example.objects.filter(L(full_name="foo bar")).count() == 1


def test_filter_by_related_lookup_property__f():
    ThingFactory.create()
    assert Thing.objects.filter(example___full_name="foo bar").count() == 1
    assert Thing.objects.filter(example___full_name="fizz buzz").count() == 0
    assert Thing.objects.filter(L(example__full_name="foo bar")).count() == 1


def test_filter_by_related_lookup_property__q():
    ThingFactory.create()
    assert Thing.objects.filter(example___q=True).count() == 1
    assert Thing.objects.filter(example___q=False).count() == 0
    assert Thing.objects.filter(L(example__q=True)).count() == 1


def test_filter_by_related_lookup_property__case():
    ThingFactory.create()
    assert Thing.objects.filter(example___case="foo").count() == 1
    assert Thing.objects.filter(example___case="bar").count() == 0
    assert Thing.objects.filter(L(example__case="foo")).count() == 1


def test_filter_by_lookup_property__only():
    ExampleFactory.create()
    assert Example.objects.filter(_full_name="foo bar").only("first_name").count() == 1
    assert Example.objects.filter(_full_name="fizz buzz").only("last_name").count() == 0
    assert Example.objects.filter(L(full_name="foo bar")).only("first_name").count() == 1


def test_filter_by_lookup_property__with_lookup_expression():
    ExampleFactory.create()
    assert Example.objects.filter(_full_name__contains="foo").count() == 1
    assert Example.objects.filter(_full_name__contains="fizz").count() == 0
    assert Example.objects.filter(L(full_name__contains="foo")).count() == 1


def test_filter_by_lookup_property__with_transform_expression():
    ExampleFactory.create()
    assert Example.objects.filter(_full_name=Upper("_full_name")).count() == 0
    assert Example.objects.filter(_full_name=Lower("_full_name")).count() == 1
    assert Example.objects.filter(L(full_name=Upper("_full_name"))).count() == 0


def test_filter_by_lookup_property__subquery():
    other = OtherFactory.create()
    ExampleFactory.create(first_name="a", last_name="a", other=other)
    ExampleFactory.create(first_name="b", last_name="b", other=other)

    subquery = Example.objects.filter(_full_name="a a").values("pk")
    assert Other.objects.filter(examples__in=models.Subquery(subquery)).count() == 1

    subquery = Example.objects.filter(L(full_name="a a")).values("pk")
    assert Other.objects.filter(examples__in=models.Subquery(subquery)).count() == 1


def test_filter_by_lookup_property__subquery__outer_ref():
    example_1 = ExampleFactory.create(first_name="a", last_name="a")
    example_2 = ExampleFactory.create(first_name="b", last_name="b")
    PartFactory.create(name="a a", examples=[example_1, example_2])

    subquery = Part.objects.filter(name=models.OuterRef("_full_name")).values("pk")
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

    subquery_1 = models.Exists(Example.objects.filter(_full_name="a a").values("pk"))
    subquery_2 = models.Exists(Example.objects.filter(_full_name="c c").values("pk"))
    other = Other.objects.annotate(has_a=subquery_1, has_c=subquery_2).first()
    assert other.has_a is True
    assert other.has_c is False


def test_filter_by_lookup_property__count__as_value():
    example = ExampleFactory.create(number=1, parts__aliens__number=1)
    assert Example.objects.filter(number=L("count_rel_many_to_many")).count() == 1
    example.number = 2
    example.save()
    assert Example.objects.filter(number=L("count_rel_many_to_many")).count() == 0


def test_filter_by_lookup_property__case_6():
    example = ExampleFactory.create(parts__far__number=1)

    assert Example.objects.count() == 1

    assert Example.objects.alias(case_6=Example.case_6.expression).filter(case_6="foo").first() == example
    assert Example.objects.alias(case_6=Example.case_6.expression).filter(case_6="bar").first() is None

    assert Example.objects.alias(case_6=L("case_6")).filter(case_6="foo").first() == example
    assert Example.objects.alias(case_6=L("case_6")).filter(case_6="bar").first() is None

    assert Example.objects.filter(L(case_6="foo")).first() == example
    assert Example.objects.filter(L(case_6="bar")).first() is None


def test_filter_by_lookup_property__case_6__multiple(query_counter):
    ExampleFactory.create(parts__far__number=1)
    ExampleFactory.create(parts__far__number=1)
    ExampleFactory.create(parts__far__number=1)
    assert Example.objects.count() == 3

    query_counter.clear()
    list(Example.objects.alias(case_6=L("case_6")).filter(case_6="foo").all())
    assert len(query_counter) == 1
    query_counter.clear()

    list(Example.objects.filter(L(case_6="foo")).all())
    assert len(query_counter) == 1


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
    assert list(Example.objects.values(case_6=L("case_6"))) == [{"case_6": "foo"}]


def test_filter_by_lookup_property__case_6__values__different_name():
    ExampleFactory.create(parts__far__number=1)
    # Not ideal, but must use an alias to avoid a collision with the `case_6` model field.
    assert list(Example.objects.values(case_6_alias=L("case_6"))) == [{"case_6_alias": "foo"}]


def test_filter_by_lookup_property__case_6__values_list():
    ExampleFactory.create(parts__far__number=1)
    assert list(Example.objects.values_list(L("case_6"))) == [("foo",)]


def test_filter_by_lookup_property__case_6__values_list_flat():
    ExampleFactory.create(parts__far__number=1)
    assert list(Example.objects.values_list(L("case_6"), flat=True)) == ["foo"]


def test_filter_by_lookup_property__case_6__annotated(query_counter):
    ExampleFactory.create(parts__far__number=1)

    query_counter.clear()
    examples = list(Example.objects.annotate(case_6=L("case_6")))
    assert len(query_counter) == 1
    # The value has been annotated in the queryset, so we don't need to calculate it again.
    assert examples[0].case_6 == "foo"
    assert len(query_counter) == 1


def test_filter_by_lookup_property__case_7():
    ExampleFactory.create(parts__number=1, parts__far__number=1)
    assert Example.objects.count() == 1

    assert Example.objects.filter(L(case_7="foo")).count() == 1
    assert Example.objects.filter(L(case_7="bar")).count() == 0


def test_filter_by_lookup_property__case_8__concrete(query_counter):
    ExampleFactory.create(parts__far__number=1)

    query_counter.clear()
    examples = list(Example.objects.all())
    assert len(query_counter) == 1
    # Concrete field was fetched with the rest of the fields
    assert examples[0].case_8 == "foo"
    assert len(query_counter) == 1


def test_filter_by_lookup_property__subquery_property():
    example = ExampleFactory.create()
    ThingFactory.create(example=example, number=1)

    assert Example.objects.filter(L(subquery=1)).count() == 1
    assert Example.objects.filter(L(subquery=2)).count() == 0


def test_filter_by_lookup_property__exists_property():
    example = ExampleFactory.create()
    TotalFactory.create(example=example, number=1)
    TotalFactory.create(example=example, number=1)

    assert Example.objects.filter(L(exists=True)).count() == 1
    assert Example.objects.filter(L(exists=False)).count() == 0


def test_filter_by_lookup_property__exists_property__from_related_model():
    example = ExampleFactory.create()
    TotalFactory.create(example=example, number=1)
    TotalFactory.create(example=example, number=1)

    assert Total.objects.filter(L(example__exists=True)).count() == 2
    assert Total.objects.filter(L(example__exists=False)).count() == 0


def test_filter_by_lookup_property__refs_another_lookup():
    ExampleFactory.create(parts__far__number=1)

    assert Example.objects.filter(L(refs_another_lookup="foo")).count() == 1
    assert Example.objects.filter(L(refs_another_lookup="bar")).count() == 0


def test_filter_by_lookup_property__refs_another_lookup__from_another_lookup():
    example = ExampleFactory.create(parts__far__number=1)
    ThingFactory.create(example=example)

    assert Thing.objects.filter(L(example__refs_another_lookup="foo")).count() == 1
    assert Thing.objects.filter(L(example__refs_another_lookup="bar")).count() == 0


def test_filter_by_lookup_property__count__aggregate_needs_group_by():
    example = ExampleFactory.create()

    # Can also alias beforehand
    assert Example.objects.alias(count_field=L("count_field")).filter(count_field=1).first() == example

    assert Example.objects.filter(L(count_field=1)).first() == example
    assert Example.objects.filter(L(count_field=0)).first() is None


def test_filter_by_lookup_property__count_rel_many_to_one():
    example = ExampleFactory.create()

    total_1 = TotalFactory.create(example=example, number=2)
    total_2 = TotalFactory.create(example=example, number=2)

    FarFactory.create(total=total_1, number=2)
    FarFactory.create(total=total_2, number=2)

    AlienFactory.create(total=total_1, number=1)
    AlienFactory.create(total=total_1, number=1)
    AlienFactory.create(total=total_2, number=1)

    assert example.count_rel_many_to_one == 3  # python code
    example = (
        Example.objects.annotate(count_rel_many_to_one=L("count_rel_many_to_one"))  #
        .filter(totals__far__number=2)
        .first()
    )
    assert example.count_rel_many_to_one == 3  # annotated value


def test_filter_by_lookup_property__count_rel_many_to_man():
    example = ExampleFactory.create()

    part_1 = PartFactory.create(examples=[example], far__number=2)
    part_2 = PartFactory.create(examples=[example], far__number=2)

    AlienFactory.create(total__example=example, parts=[part_1], number=1)
    AlienFactory.create(total__example=example, parts=[part_1], number=1)
    AlienFactory.create(total__example=example, parts=[part_2], number=1)

    assert example.count_rel_many_to_one == 3  # python code
    example = (
        Example.objects.annotate(count_rel_many_to_many=L("count_rel_many_to_many"))  #
        .filter(parts__far__number=2)
        .first()
    )
    assert example.count_rel_many_to_many == 3  # annotated value


def test_order_by_lookup_property():
    example_1 = ExampleFactory.create(first_name="1", last_name="foo")
    example_2 = ExampleFactory.create(first_name="2", last_name="foo")
    example_3 = ExampleFactory.create(first_name="3", last_name="foo")

    examples = list(Example.objects.order_by(L("full_name")))
    assert examples == [
        example_1,
        example_2,
        example_3,
    ]

    examples = list(Example.objects.order_by(L("full_name").desc()))
    assert examples == [
        example_3,
        example_2,
        example_1,
    ]


def test_filter_by_lookup_property__annotation_not_removed_by_filter():
    example = ExampleFactory.create()
    pk = example.question.pk

    # Annotation adds `forward_one_to_one` to the queryset.
    qs = Example.objects.annotate(forward_one_to_one=L("forward_one_to_one"))
    assert '"example_example"."question_id" AS "forward_one_to_one"' in str(qs.query)

    # Referring to the annotated value by string uses the annotation.
    qs = qs.filter(forward_one_to_one=pk).all()
    assert '"example_example"."question_id" AS "forward_one_to_one"' in str(qs.query)

    # Using L() to refer to the annotated value does not make the annotation an alias!
    qs = qs.filter(L(forward_one_to_one=pk)).all()
    assert '"example_example"."question_id" AS "forward_one_to_one"' in str(qs.query)


def test_filter_by_lookup_property__annotations_with_same_name_from_other_models():
    ExampleFactory.create(number=1, other__number=1)
    ExampleFactory.create(number=11, other__number=1)
    ExampleFactory.create(number=2, other__number=22)

    # This annotates the `number_in_range` property from `Example` model.
    qs = Example.objects.annotate(number_in_range=L("number_in_range"))

    # Filtering with the same lookup property works.
    assert qs.filter(L(number_in_range=True)).count() == 2

    # Filtering with a different lookup property from a different model
    # with the same name should also work, and should use the correct property.
    assert qs.filter(L(other__number_in_range=True)).count() == 1
