import datetime

from django.db import models
from django.db.models import functions
from django.db.models.functions import MD5, Random

from lookup_property import lookup_property
from lookup_property.typing import State


class Other(models.Model):
    pass


class Question(models.Model):
    pass


class Child(models.Model):
    pass


class Example(models.Model):
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    age = models.IntegerField(null=True)
    number = models.IntegerField(null=True)
    timestamp = models.DateTimeField(null=True)
    other = models.ForeignKey(Other, on_delete=models.CASCADE, related_name="examples")
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="example")
    children = models.ManyToManyField(Child, related_name="examples")

    @lookup_property(State())
    def full_name(self):
        return functions.Concat(
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def name(self):
        return models.F("full_name")

    @lookup_property
    def f_ref(self):
        return models.F("first_name")

    @lookup_property
    def combined_expression_add(self):
        return models.F("age") + 2

    @lookup_property
    def combined_expression_div(self):
        return models.F("age") / 2

    @lookup_property
    def combined_expression_mod(self):
        return models.F("age") % 2

    @lookup_property
    def combined_expression_mult(self):
        return models.F("age") * 2

    @lookup_property
    def combined_expression_pow(self):
        return models.F("age") ** 2

    @lookup_property
    def combined_expression_sub(self):
        return models.F("age") - 2

    @lookup_property
    def expression_wrapper(self):
        return models.ExpressionWrapper(
            models.F("first_name") * 2,
            output_field=models.CharField(),
        )

    @lookup_property(State(joins=True))
    def forward_one_to_one(self):
        return models.F("question__pk")

    @lookup_property(State(joins=True))
    def reverse_one_to_one(self):
        return models.F("thing__pk")

    @lookup_property(State(joins=True))
    def forward_many_to_one(self):
        return models.F("other__pk")

    @lookup_property(State(joins=True))
    def reverse_one_to_many(self):
        return models.F("totals__pk")

    @reverse_one_to_many.override
    def _(self):
        return self.totals.values_list("pk", flat=True).first()

    @lookup_property(State(joins=True))
    def forward_many_to_many(self):
        return models.F("children__pk")

    @forward_many_to_many.override
    def _(self):
        return self.children.values_list("pk", flat=True).first()

    @lookup_property(State(joins=True))
    def reverse_many_to_many(self):
        return models.F("parts__pk")

    @reverse_many_to_many.override
    def _(self):
        return self.parts.values_list("pk", flat=True).first()

    @lookup_property(State(joins=True))
    def double_join(self):
        return models.F("thing__far__pk")

    @lookup_property
    def now(self):
        return functions.Now()

    @lookup_property
    def trunc(self):
        return functions.Trunc("timestamp", "year")

    @lookup_property
    def trunc_year(self):
        return functions.TruncYear("timestamp")

    @lookup_property
    def trunc_month(self):
        return functions.TruncMonth("timestamp")

    @lookup_property
    def trunc_day(self):
        return functions.TruncDay("timestamp")

    @lookup_property
    def trunc_hour(self):
        return functions.TruncHour("timestamp")

    @lookup_property
    def trunc_minute(self):
        return functions.TruncMinute("timestamp")

    @lookup_property
    def trunc_second(self):
        return functions.TruncSecond("timestamp")

    @lookup_property
    def trunc_week(self):
        return functions.TruncWeek("timestamp")

    @lookup_property
    def trunc_quarter(self):
        return functions.TruncQuarter("timestamp")

    @lookup_property
    def trunc_date(self):
        return functions.TruncDate("timestamp")

    @lookup_property
    def trunc_time(self):
        return functions.TruncTime("timestamp")

    @lookup_property
    def upper(self):
        return functions.Upper("first_name")

    @lookup_property
    def lower(self):
        return functions.Lower("first_name")

    @lookup_property
    def lpad(self):
        return functions.LPad("first_name", length=20, fill_text=models.Value("."))

    @lookup_property
    def rpad(self):
        return functions.RPad("first_name", length=20, fill_text=models.Value("."))

    @lookup_property
    def rtrim(self):
        return functions.RTrim("first_name")

    @lookup_property
    def ltrim(self):
        return functions.LTrim("first_name")

    @lookup_property
    def length(self):
        return functions.Length("first_name")

    @lookup_property
    def concat(self):
        return functions.Concat(
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def left(self):
        return functions.Left("first_name", length=1)

    @lookup_property
    def right(self):
        return functions.Right("first_name", length=1)

    @lookup_property
    def repeat(self):
        return functions.Repeat("first_name", number=3)

    @lookup_property
    def repeat(self):
        return functions.Repeat("first_name", number=3)

    @lookup_property
    def replace(self):
        return functions.Replace("first_name", text=models.Value("oo"), replacement=models.Value("uu"))

    @lookup_property
    def reverse(self):
        return functions.Reverse("first_name")

    @lookup_property
    def strindex(self):
        return functions.StrIndex("first_name", models.Value("o"))

    @lookup_property
    def substr(self):
        return functions.Substr("first_name", 2)

    @lookup_property
    def substr_length(self):
        return functions.Substr("first_name", 2, 1)

    @lookup_property
    def trim(self):
        return functions.Trim("first_name")

    @lookup_property
    def chr_(self):
        return functions.Chr(65, output_field=models.CharField())

    @lookup_property
    def ord_(self):
        return functions.Ord("first_name", output_field=models.IntegerField())

    @lookup_property
    def md5(self):
        return MD5("first_name")

    @lookup_property
    def sha1(self):
        return functions.SHA1("first_name")

    @lookup_property
    def sha224(self):
        return functions.SHA224("first_name")

    @lookup_property
    def sha256(self):
        return functions.SHA256("first_name")

    @lookup_property
    def sha384(self):
        return functions.SHA384("first_name")

    @lookup_property
    def sha512(self):
        return functions.SHA512("first_name")

    @lookup_property
    def case(self):
        return models.Case(
            models.When(
                condition=models.Q(first_name="foo"),
                then=models.Value(1),
            ),
            default=models.Value(2),
            output_field=models.IntegerField(),
        )

    @lookup_property
    def case_2(self):
        return models.Case(
            models.When(
                condition=models.Q(first_name="fizz"),
                then=models.Value(1),
            ),
            models.When(
                condition=models.Q(last_name="bar"),
                then=models.Value(2),
            ),
            default=models.Value(3),
            output_field=models.IntegerField(),
        )

    @lookup_property
    def case_3(self):
        return models.Case(
            models.When(
                condition=models.Q(first_name="foo"),
                then=models.Case(
                    models.When(
                        condition=models.Q(last_name="bar"),
                        then=models.Value(11),
                    ),
                    default=models.Value(22),
                    output_field=models.IntegerField(),
                ),
            ),
            default=models.Case(
                models.When(
                    condition=models.Q(last_name="bar"),
                    then=models.Value(1),
                ),
                default=models.Value(2),
                output_field=models.IntegerField(),
            ),
            output_field=models.IntegerField(),
        )

    @lookup_property
    def cast_str(self):
        return functions.Cast("age", output_field=models.CharField())

    @lookup_property
    def cast_int(self):
        return functions.Cast("age", output_field=models.IntegerField())

    @lookup_property
    def cast_float(self):
        return functions.Cast("age", output_field=models.FloatField())

    @lookup_property
    def cast_decimal(self):
        return functions.Cast("age", output_field=models.DecimalField())

    @lookup_property
    def cast_bool(self):
        return functions.Cast("age", output_field=models.BooleanField())

    @lookup_property
    def cast_uuid(self):
        return functions.Cast(
            models.Value("a2cabdde-bc6b-4626-87fe-dea41458dd8f"),
            output_field=models.UUIDField(),
        )

    @lookup_property
    def cast_json(self):
        return functions.Cast(models.Value('{"foo": 1}'), output_field=models.JSONField())

    # TODO: Collate

    @lookup_property
    def coalesce(self):
        return functions.Coalesce("first_name", "last_name")

    @lookup_property
    def coalesce_2(self):
        return functions.Coalesce(functions.Concat("first_name", "last_name"), models.Value("."))

    @lookup_property
    def greatest(self):
        return functions.Greatest("age", "number")

    @lookup_property
    def least(self):
        return functions.Least("age", "number")

    @lookup_property
    def json_object(self):
        return functions.JSONObject(
            name=functions.Upper("name"),
            alias=models.Value("alias"),
            age=models.F("age") * 2,
        )

    @lookup_property
    def nullif(self):
        return functions.NullIf("first_name", "last_name")

    @lookup_property
    def extract(self):
        return functions.Extract("timestamp", "year")

    @lookup_property
    def extract_year(self):
        return functions.ExtractYear("timestamp")

    @lookup_property
    def extract_iso_year(self):
        return functions.ExtractIsoYear("timestamp")

    @lookup_property
    def extract_month(self):
        return functions.ExtractMonth("timestamp")

    @lookup_property
    def extract_day(self):
        return functions.ExtractDay("timestamp")

    @lookup_property
    def extract_week(self):
        return functions.ExtractWeek("timestamp")

    @lookup_property
    def extract_weekday(self):
        return functions.ExtractWeekDay("timestamp")

    @lookup_property
    def extract_iso_weekday(self):
        return functions.ExtractIsoWeekDay("timestamp")

    @lookup_property
    def extract_quarter(self):
        return functions.ExtractQuarter("timestamp")

    @lookup_property
    def extract_hour(self):
        return functions.ExtractHour("timestamp")

    @lookup_property
    def extract_minute(self):
        return functions.ExtractMinute("timestamp")

    @lookup_property
    def extract_second(self):
        return functions.ExtractSecond("timestamp")

    @lookup_property
    def abs_(self):
        return functions.Abs("number")

    @lookup_property
    def acos(self):
        return functions.ACos("number")

    @lookup_property
    def asin(self):
        return functions.ASin("number")

    @lookup_property
    def atan(self):
        return functions.ATan("number")

    @lookup_property
    def atan2(self):
        return functions.ATan2("number", 2)

    @lookup_property
    def ceil(self):
        return functions.Ceil("number")

    @lookup_property
    def cos(self):
        return functions.Cos("number")

    @lookup_property
    def cot(self):
        return functions.Cot("number")

    @lookup_property
    def degrees(self):
        return functions.Degrees("number")

    @lookup_property
    def exp(self):
        return functions.Exp("number")

    @lookup_property
    def floor(self):
        return functions.Floor("number")

    @lookup_property
    def ln(self):
        return functions.Ln("number")

    @lookup_property
    def log(self):
        return functions.Log("number", 10)

    @lookup_property
    def mod(self):
        return functions.Mod("number", 4)

    @lookup_property
    def pi(self):
        return functions.Pi()

    @lookup_property
    def power(self):
        return functions.Power("number", 3)

    @lookup_property
    def radians(self):
        return functions.Radians("number")

    @lookup_property
    def random(self):
        return Random()

    @lookup_property
    def round_(self):
        return functions.Round("number")

    @lookup_property
    def round_2(self):
        return functions.Round("number", precision=2)

    @lookup_property
    def sign(self):
        return functions.Sign("number")

    @lookup_property
    def sin(self):
        return functions.Sin("number")

    @lookup_property
    def sqrt(self):
        return functions.Sqrt("number")

    @lookup_property
    def tan(self):
        return functions.Tan("number")

    @lookup_property
    def q(self):
        return models.Q(first_name="foo")

    @lookup_property
    def q_neg(self):
        return ~models.Q(first_name="foo")

    @lookup_property
    def q_empty(self):
        return models.Q()

    @lookup_property
    def q_exact(self):
        return models.Q(first_name__exact="foo")

    @lookup_property
    def q_iexact(self):
        return models.Q(first_name__iexact="FOO")

    @lookup_property
    def q_iexact_null(self):
        return models.Q(first_name__iexact=None)

    @lookup_property
    def q_gte(self):
        return models.Q(timestamp__gte=functions.Now())

    @lookup_property
    def q_gt(self):
        return models.Q(timestamp__gt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))

    @lookup_property
    def q_lte(self):
        return models.Q(timestamp__lte=functions.Now())

    @lookup_property
    def q_lt(self):
        return models.Q(timestamp__lt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))

    @lookup_property
    def q_in_list(self):
        return models.Q(first_name__in=["foo", "bar"])

    @lookup_property
    def q_in_tuple(self):
        return models.Q(first_name__in=("foo", "bar"))

    @lookup_property
    def q_in_set(self):
        return models.Q(first_name__in={"foo", "bar"})

    @lookup_property
    def q_in_dict(self):
        return models.Q(first_name__in={"foo": "bar"})

    @lookup_property
    def q_contains(self):
        return models.Q(first_name__contains="fo")

    @lookup_property
    def q_icontains(self):
        return models.Q(first_name__icontains="FO")

    @lookup_property
    def q_startswith(self):
        return models.Q(first_name__startswith="fo")

    @lookup_property
    def q_istartswith(self):
        return models.Q(first_name__istartswith="FO")

    @lookup_property
    def q_endswith(self):
        return models.Q(first_name__endswith="fo")

    @lookup_property
    def q_iendswith(self):
        return models.Q(first_name__iendswith="FO")

    @lookup_property
    def q_range(self):
        return models.Q(
            timestamp__range=(
                datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC),
                datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC),
            ),
        )

    @lookup_property
    def q_isnull(self):
        return models.Q(first_name__isnull=True)

    @lookup_property
    def q_regex(self):
        return models.Q(first_name__regex=r"[a-z]*")

    @lookup_property
    def q_iregex(self):
        return models.Q(first_name__iregex=r"[A-Z]*")

    @lookup_property
    def q_or(self):
        return models.Q(first_name="foo") | models.Q(last_name="bar")

    @lookup_property
    def q_and(self):
        return models.Q(first_name="foo") & models.Q(last_name="bar")

    @lookup_property
    def q_xor(self):
        return models.Q(first_name="foo") ^ models.Q(last_name="bar")

    # @lookup_property
    # def count_field(self):
    #     return aggregates.Count("*")
    #
    # @lookup_property(State(aggregate_is_to_many=False))
    # def count_field_filter(self):
    #     return aggregates.Count("pk", filter=models.Q(number__lte=10))
    #
    # @lookup_property(State(aggregate_is_to_many=True))
    # def count_rel(self):
    #     return aggregates.Count("totals")
    #
    # @lookup_property(State(aggregate_is_to_many=True))
    # def count_rel_filter(self):
    #     return aggregates.Count("totals", filter=models.Q(totals__pk__gt=5))
    #
    # @lookup_property(State(aggregate_is_to_many=False))
    # def max_(self):
    #     return aggregates.Max("number")
    #
    # @lookup_property(State(aggregate_is_to_many=False))
    # def min_(self):
    #     return aggregates.Min("number")
    #
    # @lookup_property(State(aggregate_is_to_many=False))
    # def sum_(self):
    #     return aggregates.Sum("number")
    #
    # @lookup_property(State(aggregate_is_to_many=False))
    # def sum_filter(self):
    #     return aggregates.Sum("number", filter=models.Q(number__lte=3))


class Far(models.Model):
    name = models.CharField(max_length=256)


class Thing(models.Model):
    name = models.CharField(max_length=256)
    example = models.OneToOneField(Example, on_delete=models.CASCADE, related_name="thing")
    far = models.OneToOneField(Far, on_delete=models.CASCADE, related_name="thing")


class Total(models.Model):
    name = models.CharField(max_length=256)
    example = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="totals")
    far = models.OneToOneField(Far, on_delete=models.CASCADE, related_name="total")


class Part(models.Model):
    name = models.CharField(max_length=256)
    examples = models.ManyToManyField(Example, related_name="parts")
    far = models.OneToOneField(Far, on_delete=models.CASCADE, related_name="part")


class Abstract(models.Model):
    abstract_field = models.CharField(max_length=256)

    @lookup_property
    def abstract_property(self):
        return models.F("abstract_field")

    class Meta:
        abstract = True


class Concrete(Abstract):
    concrete_field = models.CharField(max_length=256)
