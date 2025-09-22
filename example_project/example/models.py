import datetime
import uuid
from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models import aggregates, functions
from django.db.models.functions import MD5, Random

from example_project.example.utils import SubqueryCount
from lookup_property import L, lookup_property


class Other(models.Model):
    number = models.IntegerField(null=False, default=0)

    @lookup_property
    def number_in_range() -> bool:
        return models.Q(number__gt=10)  # type: ignore[return-value]


class Question(models.Model):
    pass


class Child(models.Model): ...


class Example(models.Model):
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    age = models.IntegerField(null=True)
    number = models.IntegerField(null=True)
    timestamp = models.DateTimeField(null=True)
    other = models.ForeignKey(Other, on_delete=models.CASCADE, related_name="examples")
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="example")
    children = models.ManyToManyField(Child, related_name="examples")

    @lookup_property()
    def full_name() -> str:
        return functions.Concat(  # type: ignore[return-value]
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def number_in_range() -> bool:
        return models.Q(number__lt=10)  # type: ignore[return-value]

    @lookup_property
    def name() -> str:
        return models.F("full_name")  # type: ignore[return-value]

    @lookup_property
    def f_ref() -> str:
        return models.F("first_name")  # type: ignore[return-value]

    @lookup_property
    def combined_expression_add() -> int:
        return models.F("age") + 2

    @lookup_property
    def combined_expression_div() -> int:
        return models.F("age") / 2

    @lookup_property
    def combined_expression_mod() -> int:
        return models.F("age") % 2

    @lookup_property
    def combined_expression_mult() -> int:
        return models.F("age") * 2

    @lookup_property
    def combined_expression_pow() -> int:
        return models.F("age") ** 2

    @lookup_property
    def combined_expression_sub() -> int:
        return models.F("age") - 2

    @lookup_property
    def expression_wrapper() -> str:
        return models.ExpressionWrapper(  # type: ignore[return-value]
            models.F("first_name") * 2,
            output_field=models.CharField(),
        )

    @lookup_property(joins=["question"])
    def forward_one_to_one() -> int:
        return models.F("question__pk")  # type: ignore[return-value]

    @lookup_property(joins=["thing"])
    def reverse_one_to_one() -> int:
        return models.F("thing__pk")  # type: ignore[return-value]

    @lookup_property(joins=["other"])
    def forward_many_to_one() -> int:
        return models.F("other__pk")  # type: ignore[return-value]

    @lookup_property(joins=["totals"], skip_codegen=True)
    def reverse_one_to_many() -> int | None:
        return models.F("totals__pk")  # type: ignore[return-value]

    @reverse_one_to_many.override
    def _(self) -> int | None:
        return self.totals.values_list("pk", flat=True).first()

    @lookup_property(joins=["children"], skip_codegen=True)
    def forward_many_to_many() -> int | None:
        return models.F("children__pk")  # type: ignore[return-value]

    @forward_many_to_many.override
    def _(self) -> int | None:
        return self.children.values_list("pk", flat=True).first()

    @lookup_property(joins=["parts"], skip_codegen=True)
    def reverse_many_to_many() -> int | None:
        return models.F("parts__pk")  # type: ignore[return-value]

    @reverse_many_to_many.override
    def _(self) -> int | None:
        return self.parts.values_list("pk", flat=True).first()

    @lookup_property(joins=["thing"])
    def double_join() -> int | None:
        return models.F("thing__far__pk")  # type: ignore[return-value]

    @lookup_property
    def now() -> datetime.datetime:
        return functions.Now()  # type: ignore[return-value]

    @lookup_property
    def trunc() -> datetime.date:
        return functions.Trunc("timestamp", "year")  # type: ignore[return-value]

    @lookup_property
    def trunc_year() -> datetime.date:
        return functions.TruncYear("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_month() -> datetime.date:
        return functions.TruncMonth("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_day() -> datetime.date:
        return functions.TruncDay("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_hour() -> datetime.date:
        return functions.TruncHour("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_minute() -> datetime.date:
        return functions.TruncMinute("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_second() -> datetime.date:
        return functions.TruncSecond("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_week() -> datetime.date:
        return functions.TruncWeek("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_quarter() -> datetime.date:
        return functions.TruncQuarter("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_date() -> datetime.date:
        return functions.TruncDate("timestamp")  # type: ignore[return-value]

    @lookup_property
    def trunc_time() -> datetime.time:
        return functions.TruncTime("timestamp")  # type: ignore[return-value]

    @lookup_property
    def upper() -> str:
        return functions.Upper("first_name")  # type: ignore[return-value]

    @lookup_property
    def lower() -> str:
        return functions.Lower("first_name")  # type: ignore[return-value]

    @lookup_property
    def lpad() -> str:
        return functions.LPad("first_name", length=20, fill_text=models.Value("."))  # type: ignore[return-value]

    @lookup_property
    def rpad() -> str:
        return functions.RPad("first_name", length=20, fill_text=models.Value("."))  # type: ignore[return-value]

    @lookup_property
    def rtrim() -> str:
        return functions.RTrim("first_name")  # type: ignore[return-value]

    @lookup_property
    def ltrim() -> str:
        return functions.LTrim("first_name")  # type: ignore[return-value]

    @lookup_property
    def length() -> int:
        return functions.Length("first_name")  # type: ignore[return-value]

    @lookup_property
    def concat() -> str:
        return functions.Concat(  # type: ignore[return-value]
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def left() -> str:
        return functions.Left("first_name", length=1)  # type: ignore[return-value]

    @lookup_property
    def right() -> str:
        return functions.Right("first_name", length=1)  # type: ignore[return-value]

    @lookup_property
    def repeat() -> str:
        return functions.Repeat("first_name", number=3)  # type: ignore[return-value]

    @lookup_property
    def replace() -> str:
        return functions.Replace("first_name", text=models.Value("oo"), replacement=models.Value("uu"))  # type: ignore[return-value]

    @lookup_property
    def reverse() -> str:
        return functions.Reverse("first_name")  # type: ignore[return-value]

    @lookup_property
    def strindex() -> int:
        return functions.StrIndex("first_name", models.Value("o"))  # type: ignore[return-value]

    @lookup_property
    def substr() -> str:
        return functions.Substr("first_name", 2)  # type: ignore[return-value]

    @lookup_property
    def substr_length() -> str:
        return functions.Substr("first_name", 2, 1)  # type: ignore[return-value]

    @lookup_property
    def trim() -> str:
        return functions.Trim("first_name")  # type: ignore[return-value]

    @lookup_property
    def chr_() -> str:
        return functions.Chr(65, output_field=models.CharField())  # type: ignore[return-value]

    @lookup_property
    def ord_() -> int:
        return functions.Ord("first_name", output_field=models.IntegerField())  # type: ignore[return-value]

    @lookup_property
    def md5() -> str:
        return MD5("first_name")  # type: ignore[return-value]

    @lookup_property
    def sha1() -> str:
        return functions.SHA1("first_name")  # type: ignore[return-value]

    @lookup_property
    def sha224() -> str:
        return functions.SHA224("first_name")  # type: ignore[return-value]

    @lookup_property
    def sha256() -> str:
        return functions.SHA256("first_name")  # type: ignore[return-value]

    @lookup_property
    def sha384() -> str:
        return functions.SHA384("first_name")  # type: ignore[return-value]

    @lookup_property
    def sha512() -> str:
        return functions.SHA512("first_name")  # type: ignore[return-value]

    @lookup_property
    def case() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                models.Q(first_name="foo"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_2() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(first_name="fizz"),
                then=models.Value("foo"),
            ),
            models.When(
                condition=models.Q(last_name="bar"),
                then=models.Value("bar"),
            ),
            default=models.Value("baz"),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_3() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(first_name="foo"),
                then=models.Case(
                    models.When(
                        condition=models.Q(last_name="bar"),
                        then=models.Value("fizz"),
                    ),
                    default=models.Value("buzz"),
                    output_field=models.CharField(),
                ),
            ),
            default=models.Case(
                models.When(
                    condition=models.Q(last_name="bar"),
                    then=models.Value("foo"),
                ),
                default=models.Value("bar"),
                output_field=models.CharField(),
            ),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_4() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(first_name="foo") & models.Q(last_name="bar"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property(skip_codegen=True)
    def case_5() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(totals__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value(2),
            output_field=models.CharField(),
        )

    @case_5.override
    def _(self) -> str:
        return "foo" if self.totals.filter(number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True)
    def case_6() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_6.override
    def _(self) -> str:
        return "foo" if self.parts.filter(far__number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True)
    def case_7() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(parts__number=1) & models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_7.override
    def _(self) -> str:
        return "foo" if self.parts.filter(number=1, far__number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True, concrete=True)
    def case_8() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_8.override
    def _(self) -> str:
        return "foo" if self.parts.filter(far__number=1).exists() else "bar"

    @lookup_property
    def case_9() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(first_name="foo") & models.Q(last_name="bar") | models.Q(age=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_10() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                condition=models.Q(first_name="foo") & (models.Q(last_name="bar") | ~models.Q(age=1)),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property(skip_codegen=True)
    def reffed_by_another_lookup() -> str:
        return models.F("parts__far__number")  # type: ignore[return-value]

    @reffed_by_another_lookup.override
    def _(self) -> str:
        return self.parts.values_list("far__number", flat=True).first()

    @lookup_property
    def refs_another_lookup() -> str:
        return models.Case(  # type: ignore[return-value]
            models.When(
                models.Q(L(reffed_by_another_lookup=1)),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def cast_str() -> str:
        return functions.Cast("age", output_field=models.CharField())  # type: ignore[return-value]

    @lookup_property
    def cast_int() -> int:
        return functions.Cast("age", output_field=models.IntegerField())  # type: ignore[return-value]

    @lookup_property
    def cast_float() -> float:
        return functions.Cast("age", output_field=models.FloatField())  # type: ignore[return-value]

    @lookup_property
    def cast_decimal() -> Decimal:
        return functions.Cast("age", output_field=models.DecimalField())  # type: ignore[return-value]

    @lookup_property
    def cast_bool() -> bool:
        return functions.Cast("age", output_field=models.BooleanField())  # type: ignore[return-value]

    @lookup_property
    def cast_uuid() -> uuid.UUID:
        return functions.Cast(  # type: ignore[return-value]
            models.Value("a2cabdde-bc6b-4626-87fe-dea41458dd8f"),
            output_field=models.UUIDField(),
        )

    @lookup_property
    def cast_json() -> dict[str, Any]:
        return functions.Cast(models.Value('{"foo": 1}'), output_field=models.JSONField())  # type: ignore[return-value]

    # TODO: Collate

    @lookup_property
    def coalesce() -> str:
        return functions.Coalesce("first_name", "last_name")  # type: ignore[return-value]

    @lookup_property
    def coalesce_2() -> str:
        return functions.Coalesce(functions.Concat("first_name", "last_name"), models.Value("."))  # type: ignore[return-value]

    @lookup_property
    def greatest() -> int:
        return functions.Greatest("age", "number")  # type: ignore[return-value]

    @lookup_property
    def least() -> int:
        return functions.Least("age", "number")  # type: ignore[return-value]

    @lookup_property
    def json_object() -> dict[str, Any]:
        return functions.JSONObject(  # type: ignore[return-value]
            name=functions.Upper("name"),
            alias=models.Value("alias"),
            age=models.F("age") * 2,
        )

    @lookup_property
    def nullif() -> str:
        return functions.NullIf("first_name", "last_name")  # type: ignore[return-value]

    @lookup_property
    def extract() -> int:
        return functions.Extract("timestamp", "year")  # type: ignore[return-value]

    @lookup_property
    def extract_year() -> int:
        return functions.ExtractYear("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_iso_year() -> int:
        return functions.ExtractIsoYear("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_month() -> int:
        return functions.ExtractMonth("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_day() -> int:
        return functions.ExtractDay("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_week() -> int:
        return functions.ExtractWeek("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_weekday() -> int:
        return functions.ExtractWeekDay("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_iso_weekday() -> int:
        return functions.ExtractIsoWeekDay("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_quarter() -> int:
        return functions.ExtractQuarter("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_hour() -> int:
        return functions.ExtractHour("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_minute() -> int:
        return functions.ExtractMinute("timestamp")  # type: ignore[return-value]

    @lookup_property
    def extract_second() -> int:
        return functions.ExtractSecond("timestamp")  # type: ignore[return-value]

    @lookup_property
    def abs_() -> float:
        return functions.Abs("number")  # type: ignore[return-value]

    @lookup_property
    def acos() -> float:
        return functions.ACos("number")  # type: ignore[return-value]

    @lookup_property
    def asin() -> float:
        return functions.ASin("number")  # type: ignore[return-value]

    @lookup_property
    def atan() -> float:
        return functions.ATan("number")  # type: ignore[return-value]

    @lookup_property
    def atan2() -> float:
        return functions.ATan2("number", 2)  # type: ignore[return-value]

    @lookup_property
    def ceil() -> float:
        return functions.Ceil("number")  # type: ignore[return-value]

    @lookup_property
    def cos() -> float:
        return functions.Cos("number")  # type: ignore[return-value]

    @lookup_property
    def cot() -> float:
        return functions.Cot("number")  # type: ignore[return-value]

    @lookup_property
    def degrees() -> float:
        return functions.Degrees("number")  # type: ignore[return-value]

    @lookup_property
    def exp() -> float:
        return functions.Exp("number")  # type: ignore[return-value]

    @lookup_property
    def floor() -> float:
        return functions.Floor("number")  # type: ignore[return-value]

    @lookup_property
    def ln() -> float:
        return functions.Ln("number")  # type: ignore[return-value]

    @lookup_property
    def log() -> float:
        return functions.Log("number", 10)  # type: ignore[return-value]

    @lookup_property
    def mod() -> int:
        return functions.Mod("number", 4)  # type: ignore[return-value]

    @lookup_property
    def pi() -> float:
        return functions.Pi()  # type: ignore[return-value]

    @lookup_property
    def power() -> int:
        return functions.Power("number", 3)  # type: ignore[return-value]

    @lookup_property
    def radians() -> float:
        return functions.Radians("number")  # type: ignore[return-value]

    @lookup_property
    def random() -> float:
        return Random()  # type: ignore[return-value]

    @lookup_property
    def round_() -> float:
        return functions.Round("number")  # type: ignore[return-value]

    @lookup_property
    def round_2() -> float:
        return functions.Round("number", precision=2)  # type: ignore[return-value]

    @lookup_property
    def sign() -> float:
        return functions.Sign("number")  # type: ignore[return-value]

    @lookup_property
    def sin() -> float:
        return functions.Sin("number")  # type: ignore[return-value]

    @lookup_property
    def sqrt() -> float:
        return functions.Sqrt("number")  # type: ignore[return-value]

    @lookup_property
    def tan() -> float:
        return functions.Tan("number")  # type: ignore[return-value]

    @lookup_property
    def q() -> bool:
        return models.Q(first_name="foo")  # type: ignore[return-value]

    @lookup_property
    def q_rel() -> bool:
        return models.Q(thing__name="foo")  # type: ignore[return-value]

    @lookup_property
    def q_neg() -> bool:
        return ~models.Q(first_name="foo")  # type: ignore[return-value]

    @lookup_property
    def q_empty() -> bool:
        return models.Q()  # type: ignore[return-value]

    @lookup_property
    def q_exact() -> bool:
        return models.Q(first_name__exact="foo")  # type: ignore[return-value]

    @lookup_property
    def q_iexact() -> bool:
        return models.Q(first_name__iexact="FOO")  # type: ignore[return-value]

    @lookup_property
    def q_iexact_null() -> bool:
        return models.Q(first_name__iexact=None)  # type: ignore[return-value]

    @lookup_property
    def q_gte() -> bool:
        return models.Q(timestamp__gte=functions.Now())  # type: ignore[return-value]

    @lookup_property
    def q_gt() -> bool:
        return models.Q(timestamp__gt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))  # type: ignore[return-value]

    @lookup_property
    def q_lte() -> bool:
        return models.Q(timestamp__lte=functions.Now())  # type: ignore[return-value]

    @lookup_property
    def q_lt() -> bool:
        return models.Q(timestamp__lt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))  # type: ignore[return-value]

    @lookup_property
    def q_in_list() -> bool:
        return models.Q(first_name__in=["foo", "bar"])  # type: ignore[return-value]

    @lookup_property
    def q_in_tuple() -> bool:
        return models.Q(first_name__in=("foo", "bar"))  # type: ignore[return-value]

    @lookup_property
    def q_in_set() -> bool:
        return models.Q(first_name__in={"foo", "bar"})  # type: ignore[return-value]

    @lookup_property
    def q_in_dict() -> bool:
        return models.Q(first_name__in={"foo": "bar"})  # type: ignore[return-value]

    @lookup_property
    def q_contains() -> bool:
        return models.Q(first_name__contains="fo")  # type: ignore[return-value]

    @lookup_property
    def q_icontains() -> bool:
        return models.Q(first_name__icontains="FO")  # type: ignore[return-value]

    @lookup_property
    def q_startswith() -> bool:
        return models.Q(first_name__startswith="fo")  # type: ignore[return-value]

    @lookup_property
    def q_istartswith() -> bool:
        return models.Q(first_name__istartswith="FO")  # type: ignore[return-value]

    @lookup_property
    def q_endswith() -> bool:
        return models.Q(first_name__endswith="fo")  # type: ignore[return-value]

    @lookup_property
    def q_iendswith() -> bool:
        return models.Q(first_name__iendswith="FO")  # type: ignore[return-value]

    @lookup_property
    def q_range() -> bool:
        return models.Q(  # type: ignore[return-value]
            timestamp__range=(
                datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC),
                datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC),
            ),
        )

    @lookup_property
    def q_isnull() -> bool:
        return models.Q(first_name__isnull=True)  # type: ignore[return-value]

    @lookup_property
    def q_regex() -> bool:
        return models.Q(first_name__regex=r"[a-z]*")  # type: ignore[return-value]

    @lookup_property
    def q_iregex() -> bool:
        return models.Q(first_name__iregex=r"[A-Z]*")  # type: ignore[return-value]

    @lookup_property
    def q_or() -> bool:
        return models.Q(first_name="foo") | models.Q(last_name="bar")  # type: ignore[return-value]

    @lookup_property
    def q_and() -> bool:
        return models.Q(first_name="foo") & models.Q(last_name="bar")  # type: ignore[return-value]

    @lookup_property
    def q_xor() -> bool:
        return models.Q(first_name="foo") ^ models.Q(last_name="bar")  # type: ignore[return-value]

    @lookup_property
    def count_field() -> int:
        return aggregates.Count("*")  # type: ignore[return-value]

    @lookup_property
    def count_field_filter() -> int:
        return aggregates.Count("pk", filter=models.Q(number__lte=10))  # type: ignore[return-value]

    @lookup_property
    def count_rel() -> int:
        return aggregates.Count("totals__pk")  # type: ignore[return-value]

    @lookup_property
    def count_rel_filter() -> int:
        return aggregates.Count("totals", filter=models.Q(totals__name__contains="bar"))  # type: ignore[return-value]

    @lookup_property(skip_codegen=True)
    def count_rel_many_to_one() -> int:
        # `aggregates.Count("totals__aliens")` does not work correctly together with filtering.
        # See: `tests.test_filtering.test_filter_by_lookup_property__count_rel_many_to_one`
        return SubqueryCount(Alien.objects.filter(total__example=models.OuterRef("pk")).values("id"))  # type: ignore[return-value]

    @count_rel_many_to_one.override
    def _(self) -> int:
        return self.totals.aggregate(_count=models.Count("aliens"))["_count"]

    @lookup_property(skip_codegen=True)
    def count_rel_many_to_many() -> int:
        # `aggregates.Count("parts__aliens")` does not work correctly together with filtering
        # See: `tests.test_filtering.test_filter_by_lookup_property__count_rel_many_to_many`
        return SubqueryCount(Alien.objects.filter(parts__examples=models.OuterRef("pk")).values("id"))  # type: ignore[return-value]

    @count_rel_many_to_many.override
    def _(self) -> int:
        return self.parts.aggregate(_count=models.Count("aliens"))["_count"]

    @lookup_property
    def max_() -> int:
        return aggregates.Max("number")  # type: ignore[return-value]

    @lookup_property
    def max_rel() -> int:
        return aggregates.Max("totals__number")  # type: ignore[return-value]

    @lookup_property
    def min_() -> int:
        return aggregates.Min("number")  # type: ignore[return-value]

    @lookup_property
    def min_rel() -> int:
        return aggregates.Min("totals__number")  # type: ignore[return-value]

    @lookup_property
    def sum_() -> int:
        return aggregates.Sum("number")  # type: ignore[return-value]

    @lookup_property
    def sum_rel() -> int:
        return aggregates.Sum("totals__number")  # type: ignore[return-value]

    @lookup_property
    def sum_filter() -> int:
        return aggregates.Sum("number", filter=models.Q(number__lte=3))  # type: ignore[return-value]

    @lookup_property
    def avg() -> int:
        return aggregates.Avg("number")  # type: ignore[return-value]

    @lookup_property
    def std_dev() -> float:
        return aggregates.StdDev("number")  # type: ignore[return-value]

    @lookup_property
    def variance() -> float:
        return aggregates.Variance("number")  # type: ignore[return-value]

    @lookup_property(skip_codegen=True)
    def subquery() -> int:
        return models.Subquery(Thing.objects.filter(example=models.OuterRef("pk")).values("number")[:1])  # type: ignore[return-value]

    @subquery.override
    def _(self) -> int:
        return self.thing.number

    @lookup_property(skip_codegen=True)
    def exists() -> bool:
        return models.Exists(Total.objects.filter(example=models.OuterRef("pk"), number=1))  # type: ignore[return-value]

    @exists.override
    def _(self) -> bool:
        return Total.objects.filter(example=self, number=1).exists()


class Far(models.Model):
    name = models.CharField(max_length=256)
    number = models.IntegerField(null=True)
    total = models.OneToOneField("Total", on_delete=models.CASCADE, related_name="far")


class Alien(models.Model):
    name = models.CharField(max_length=256)
    number = models.IntegerField(null=True)
    total = models.ForeignKey("Total", on_delete=models.CASCADE, related_name="aliens")
    parts = models.ManyToManyField("Part", related_name="aliens")


class Thing(models.Model):
    name = models.CharField(max_length=256)
    number = models.IntegerField(null=True)
    example = models.OneToOneField(Example, on_delete=models.CASCADE, related_name="thing")
    far = models.OneToOneField(Far, on_delete=models.CASCADE, related_name="thing")
    aliens = models.ManyToManyField(Alien, related_name="things")

    @lookup_property
    def number_in_range() -> bool:
        return models.Q(number__gt=10)  # type: ignore[return-value]


class Total(models.Model):
    name = models.CharField(max_length=256)
    number = models.IntegerField(null=True)
    example = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="totals")


class Part(models.Model):
    name = models.CharField(max_length=256)
    number = models.IntegerField(null=True)
    examples = models.ManyToManyField(Example, related_name="parts")
    far = models.ForeignKey(Far, on_delete=models.CASCADE, related_name="parts")


class Abstract(models.Model):
    abstract_field = models.CharField(max_length=256)

    class Meta:
        abstract = True

    @lookup_property
    def abstract_property() -> str:
        return models.F("abstract_field")  # type: ignore[return-value]


class AnotherAbstract(Abstract):
    another_abstract_field = models.CharField(max_length=256)

    class Meta:
        abstract = True

    @lookup_property
    def another_abstract_property() -> str:
        return models.F("another_abstract_field")  # type: ignore[return-value]


class Concrete(Abstract):
    concrete_field = models.CharField(max_length=256)


class AnotherConcrete(AnotherAbstract):
    another_concrete_field = models.CharField(max_length=256)
