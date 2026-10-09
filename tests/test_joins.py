from typing import Any

import pytest
from django.db.models import Case, Count, Exists, F, Max, OuterRef, Q, QuerySet, Subquery, Value, When

from example_project.example.models import Child, Example, Far, Thing, Total
from lookup_property import L, lookup_property
from tests.factories import ChildFactory, ExampleFactory, FarFactory, PartFactory, ThingFactory, TotalFactory

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def data() -> dict[str, Any]:
    # Create extra rows first, so that primary keys in different tables don't match by chance.
    for _ in range(3):
        FarFactory.create()

    e1 = ExampleFactory.create(first_name="e1")
    e2 = ExampleFactory.create(first_name="e2")
    e3 = ExampleFactory.create(first_name="e3")  # No related objects.
    far = FarFactory.create(number=1)
    t1 = ThingFactory.create(example=e1, far=far)
    t2 = ThingFactory.create(example=e2)
    tot_a = TotalFactory.create(example=e1)
    tot_b = TotalFactory.create(example=e1)
    tot_c = TotalFactory.create(example=e2)
    child = ChildFactory.create()
    e1.children.add(child)
    part = PartFactory.create(far=far, number=1)
    part.examples.add(e1)

    assert t1.pk != far.pk
    return {
        "e1": e1,
        "e2": e2,
        "e3": e3,
        "far": far,
        "t1": t1,
        "t2": t2,
        "tot_a": tot_a,
        "tot_b": tot_b,
        "tot_c": tot_c,
        "child": child,
        "part": part,
    }


def names(qs: QuerySet[Example]) -> list[str]:
    return sorted(qs.filter(first_name__in=["e1", "e2", "e3"]).values_list("first_name", flat=True))


def test_joins__filter(data):
    assert names(Example.objects.filter(L(double_join=data["far"].pk))) == ["e1"]
    assert names(Example.objects.filter(L(reverse_one_to_one=data["t2"].pk))) == ["e2"]
    assert names(Example.objects.filter(L(reverse_one_to_many=data["tot_b"].pk))) == ["e1"]
    assert names(Example.objects.filter(L(forward_many_to_many=data["child"].pk))) == ["e1"]
    assert names(Example.objects.filter(L(reverse_many_to_many=data["part"].pk))) == ["e1"]
    assert names(Example.objects.filter(L(case_6="foo"))) == ["e1"]
    assert names(Example.objects.filter(L(case_7="foo"))) == ["e1"]


def test_joins__filter__count(data):
    assert Example.objects.filter(L(double_join=data["far"].pk)).count() == 1
    assert Example.objects.filter(L(reverse_one_to_many=data["tot_b"].pk)).count() == 1
    assert Example.objects.filter(L(case_6="foo")).count() == 1


def test_joins__filter__multi_valued__no_duplicate_rows(data):
    qs = Example.objects.filter(L(reverse_one_to_many__in=[data["tot_a"].pk, data["tot_b"].pk]))
    assert list(qs) == [data["e1"]]


def test_joins__filter__or(data):
    qs = Example.objects.filter(L(double_join=data["far"].pk) | Q(first_name="e3"))
    assert names(qs) == ["e1", "e3"]

    qs = Example.objects.filter(Q(first_name="e3") | L(reverse_one_to_many=data["tot_c"].pk))
    assert names(qs) == ["e2", "e3"]


def test_joins__filter__chained__multi_valued(data):
    qs = Example.objects.filter(L(reverse_one_to_many=data["tot_a"].pk))
    qs = qs.filter(L(reverse_one_to_many=data["tot_b"].pk))
    assert names(qs) == ["e1"]


def test_joins__filter__same_call__multi_valued(data):
    # Each lookup property has its own value, so both conditions don't need to match the same related row.
    qs = Example.objects.filter(L(reverse_one_to_many=data["tot_a"].pk), L(reverse_one_to_many=data["tot_b"].pk))
    assert names(qs) == ["e1"]


def test_joins__filter__isnull(data):
    assert names(Example.objects.filter(L(reverse_one_to_one__isnull=True))) == ["e3"]
    assert names(Example.objects.filter(L(reverse_one_to_one__isnull=False))) == ["e1", "e2"]


def test_joins__filter__f_value(data):
    Example.objects.filter(pk=data["e1"].pk).update(number=data["tot_b"].pk)
    assert names(Example.objects.filter(L(reverse_one_to_many=F("number")))) == ["e1"]
    assert names(Example.objects.exclude(L(reverse_one_to_many=F("number")))) == ["e2", "e3"]


def test_joins__filter__outer_ref_value(data):
    sq = Example.objects.filter(L(reverse_one_to_many=OuterRef("pk")), first_name="e1")
    qs = Total.objects.filter(Exists(sq)).order_by("pk")
    assert list(qs) == [data["tot_a"], data["tot_b"]]


def test_joins__filter__outer_ref_value__in_list(data):
    sq = Example.objects.filter(L(reverse_one_to_many__in=[OuterRef("pk")]), first_name="e1")
    qs = Total.objects.filter(Exists(sq)).order_by("pk")
    assert list(qs) == [data["tot_a"], data["tot_b"]]


def test_joins__filter__aggregate(data):
    assert names(Example.objects.filter(L(count_rel=2))) == ["e1"]
    assert names(Example.objects.exclude(L(count_rel=2))) == ["e2", "e3"]


def test_joins__exclude(data):
    assert names(Example.objects.exclude(L(double_join=data["far"].pk))) == ["e2", "e3"]
    assert names(Example.objects.filter(~L(double_join=data["far"].pk))) == ["e2", "e3"]
    assert names(Example.objects.filter(~Q(L(double_join=data["far"].pk)))) == ["e2", "e3"]


def test_joins__exclude__multi_valued(data):
    # 'e1' has two totals. It should be excluded if any of them matches.
    assert names(Example.objects.exclude(L(reverse_one_to_many=data["tot_a"].pk))) == ["e2", "e3"]
    assert names(Example.objects.filter(~L(reverse_one_to_many=data["tot_a"].pk))) == ["e2", "e3"]


def test_joins__exclude__null_values(data):
    # 'e3' has no thing, so 'double_join' is NULL for it. NULL is not equal to the value.
    assert "e3" in names(Example.objects.exclude(L(double_join=data["far"].pk)))
    assert "e3" in names(Example.objects.exclude(L(case_6="foo")))


def test_joins__annotate(data):
    qs = Example.objects.annotate(value=L("double_join"))
    values = dict(qs.filter(first_name__in=["e1", "e2", "e3"]).values_list("first_name", "value"))
    assert values == {"e1": data["far"].pk, "e2": data["t2"].far_id, "e3": None}


def test_joins__annotate__multi_valued__no_duplicate_rows(data):
    qs = Example.objects.filter(first_name__in=["e1", "e2", "e3"]).annotate(value=L("reverse_one_to_many"))
    values = dict(qs.values_list("first_name", "value"))
    assert len(qs) == 3
    assert values["e1"] in {data["tot_a"].pk, data["tot_b"].pk}
    assert values["e2"] == data["tot_c"].pk
    assert values["e3"] is None


def test_joins__values_list(data):
    qs = Example.objects.filter(first_name__in=["e1", "e2"]).order_by("first_name")
    assert list(qs.values_list(L("double_join"), flat=True)) == [data["far"].pk, data["t2"].far_id]


def test_joins__order_by(data):
    qs = Example.objects.filter(first_name__in=["e1", "e2"])
    expected = sorted(qs, key=lambda example: example.double_join, reverse=True)
    assert list(qs.order_by(L("double_join").desc())) == expected

    qs = Example.objects.filter(first_name__in=["e1", "e2", "e3"])
    assert len(qs.order_by(L("reverse_one_to_many").asc())) == 3


def test_joins__aggregate(data):
    qs = Example.objects.filter(first_name__in=["e1", "e2"])
    assert qs.aggregate(value=Max(L("double_join")))["value"] == max(data["far"].pk, data["t2"].far_id)


def test_joins__filter_and_annotate__reuse_join(data, query_counter):
    qs = Example.objects.filter(L(double_join=data["far"].pk)).annotate(value=L("double_join"))
    assert list(qs.values_list("first_name", "value")) == [("e1", data["far"].pk)]
    assert query_counter[0].count("JOIN") == 1


def test_joins__value_in_filter(data):
    Example.objects.filter(pk=data["e1"].pk).update(number=data["far"].pk)
    assert names(Example.objects.filter(number=L("double_join"))) == ["e1"]


def test_joins__related_lookup(data):
    assert list(Thing.objects.filter(L(example__double_join=data["far"].pk))) == [data["t1"]]
    assert list(Far.objects.filter(L(thing__example__reverse_one_to_many=data["tot_b"].pk))) == [data["far"]]
    assert list(Total.objects.filter(L(example__case_6="foo")).order_by("pk")) == [data["tot_a"], data["tot_b"]]


def test_joins__related_lookup__exclude__multi_valued(data):
    other_child = Child.objects.create()
    data["e2"].children.add(other_child)
    qs = Child.objects.filter(pk__in=[data["child"].pk, other_child.pk])
    assert list(qs.exclude(L(examples__full_name="e1 bar"))) == [other_child]


def test_joins__subquery(data):
    sq = Example.objects.filter(L(double_join=data["far"].pk)).values("pk")
    assert list(Thing.objects.filter(example__in=sq)) == [data["t1"]]


def test_joins__update_and_delete(data):
    assert Example.objects.filter(L(double_join=data["far"].pk)).update(age=99) == 1
    assert Example.objects.get(pk=data["e1"].pk).age == 99

    Total.objects.filter(L(example__double_join=data["far"].pk)).delete()
    assert not Total.objects.filter(example=data["e1"]).exists()


def test_joins__concrete(data):
    assert Example.objects.get(pk=data["e1"].pk).case_8 == "foo"
    assert Example.objects.get(pk=data["e2"].pk).case_8 == "bar"


def test_joins__concrete__multi_valued__no_duplicate_rows(data):
    PartFactory.create(examples=[data["e1"]])
    qs = Example.objects.filter(pk=data["e1"].pk)
    assert len(qs) == qs.count() == 1


def test_joins__concrete__select_related(data):
    thing = Thing.objects.select_related("example").get(pk=data["t1"].pk)
    assert thing.example.case_8 == "foo"


def test_joins__concrete__select_related__two_levels(data):
    far = Far.objects.select_related("thing__example").get(pk=data["far"].pk)
    assert far.thing.example.case_8 == "foo"


def test_joins__concrete__select_related__table_joined_twice(data):
    # 'example_example' is joined first through 'total', so 'thing__example' gets a different alias.
    far = FarFactory.create(total__example=data["e2"])
    ThingFactory.create(example=data["e3"], far=far)
    data["part"].examples.add(data["e3"])  # 'case_8' is "foo" for 'e3', but "bar" for 'e2'.
    far = Far.objects.filter(total__example__first_name="e2").select_related("thing__example").get()
    assert far.thing.example == data["e3"]
    assert far.thing.example.case_8 == "foo"


def test_joins__concrete__in_subquery(data):
    sq = Example.objects.filter(pk=OuterRef("example")).values("_lookup_property_case_8")[:1]
    values = dict(Thing.objects.annotate(value=Subquery(sq)).values_list("pk", "value"))
    assert values[data["t1"].pk] == "foo"
    assert values[data["t2"].pk] == "bar"


def test_joins__concrete__in_nested_subquery(data):
    inner = Example.objects.filter(pk=OuterRef("example")).values("_lookup_property_case_8")[:1]
    middle = Thing.objects.filter(far=OuterRef("pk")).annotate(value=Subquery(inner)).values("value")[:1]
    values = dict(Far.objects.annotate(value=Subquery(middle)).values_list("pk", "value"))
    assert values[data["far"].pk] == "foo"
    assert values[data["t2"].far_id] == "bar"


def test_joins__concrete__wrapped_queries(data):
    assert Example.objects.all()[:2].count() == 2
    assert Example.objects.distinct().count() == Example.objects.count()
    assert Example.objects.annotate(count=Count("totals")).get(pk=data["e1"].pk).count == 2

    qs = Example.objects.filter(pk=data["e1"].pk).union(Example.objects.filter(pk=data["e2"].pk))
    assert sorted(example.case_8 for example in qs) == ["bar", "foo"]


def test_joins__concrete__refresh_and_save(data):
    example = Example.objects.get(pk=data["e1"].pk)
    example.refresh_from_db()
    assert example.case_8 == "foo"

    example.age = 5
    example.save()
    example.refresh_from_db(fields=["age"])
    assert example.age == 5


def test_joins__lookup_property_col(data):
    # The lookup property field should be resolved for the correct table, even through relations.
    assert names(Example.objects.filter(_lookup_property_double_join=data["far"].pk)) == ["e1"]
    assert list(Thing.objects.filter(example___lookup_property_double_join=data["far"].pk)) == [data["t1"]]


def test_joins__deprecated_argument():
    with pytest.deprecated_call(match="The `joins` argument is deprecated"):

        @lookup_property(joins=["thing"])
        def foo() -> int:
            return F("thing__pk")  # type: ignore[return-value]

