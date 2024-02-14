import datetime

from django.db import models
from django.db.models import aggregates, functions
from django.db.models.functions import MD5, Random

from lookup_property import lookup_property, L


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

    @lookup_property()
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

    @lookup_property(joins=True)
    def forward_one_to_one(self):
        return models.F("question__pk")

    @lookup_property(joins=True)
    def reverse_one_to_one(self):
        return models.F("thing__pk")

    @lookup_property(joins=True)
    def forward_many_to_one(self):
        return models.F("other__pk")

    @lookup_property(joins=True, skip_codegen=True)
    def reverse_one_to_many(self):
        return models.F("totals__pk")

    @reverse_one_to_many.override
    def _(self):
        return self.totals.values_list("pk", flat=True).first()

    @lookup_property(joins=True, skip_codegen=True)
    def forward_many_to_many(self):
        return models.F("children__pk")

    @forward_many_to_many.override
    def _(self):
        return self.children.values_list("pk", flat=True).first()

    @lookup_property(joins=True, skip_codegen=True)
    def reverse_many_to_many(self):
        return models.F("parts__pk")

    @reverse_many_to_many.override
    def _(self):
        return self.parts.values_list("pk", flat=True).first()

    @lookup_property(joins=True)
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
                models.Q(first_name="foo"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_2(self):
        return models.Case(
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
    def case_3(self):
        return models.Case(
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
    def case_4(self):
        return models.Case(
            models.When(
                condition=models.Q(first_name="foo") & models.Q(last_name="bar"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property(skip_codegen=True)
    def case_5(self):
        return models.Case(
            models.When(
                condition=models.Q(totals__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value(2),
            output_field=models.CharField(),
        )

    @case_5.override
    def _(self):
        return "foo" if self.totals.filter(number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True)
    def case_6(self):
        return models.Case(
            models.When(
                models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_6.override
    def _(self):
        return "foo" if self.parts.filter(far__number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True)
    def case_7(self):
        return models.Case(
            models.When(
                condition=models.Q(parts__number=1) & models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_7.override
    def _(self):
        return "foo" if self.parts.filter(number=1, far__number=1).exists() else "bar"

    @lookup_property(joins=["parts"], skip_codegen=True, concrete=True)
    def case_8(self):
        return models.Case(
            models.When(
                models.Q(parts__far__number=1),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @case_8.override
    def _(self):
        return "foo" if self.parts.filter(far__number=1).exists() else "bar"

    @lookup_property(joins=["parts"])
    def reffed_by_another_lookup(self):
        return models.F("parts__far__number")

    @lookup_property(joins=["parts"], skip_codegen=True)
    def refs_another_lookup(self):
        return models.Case(
            models.When(
                models.Q(L(reffed_by_another_lookup=1)),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @refs_another_lookup.override
    def _(self):
        return "foo" if self.parts.filter(far__number=1).exists() else "bar"

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

    @lookup_property
    def count_field(self):
        return aggregates.Count("*")

    @lookup_property
    def count_field_filter(self):
        return aggregates.Count("pk", filter=models.Q(number__lte=10))

    @lookup_property
    def count_rel(self):
        return aggregates.Count("totals__pk")

    @lookup_property(joins=True)
    def count_rel_deep(self):
        return aggregates.Count("parts__aliens")

    @lookup_property
    def count_rel_filter(self):
        return aggregates.Count("totals", filter=models.Q(totals__name__contains="bar"))

    @lookup_property
    def max_(self):
        return aggregates.Max("number")

    @lookup_property
    def max_rel(self):
        return aggregates.Max("totals__number")

    @lookup_property
    def min_(self):
        return aggregates.Min("number")

    @lookup_property
    def min_rel(self):
        return aggregates.Min("totals__number")

    @lookup_property
    def sum_(self):
        return aggregates.Sum("number")

    @lookup_property
    def sum_rel(self):
        return aggregates.Sum("totals__number")

    @lookup_property
    def sum_filter(self):
        return aggregates.Sum("number", filter=models.Q(number__lte=3))

    @lookup_property
    def avg(self):
        return aggregates.Avg("number")

    @lookup_property
    def std_dev(self):
        return aggregates.StdDev("number")

    @lookup_property
    def variance(self):
        return aggregates.Variance("number")

    @lookup_property(skip_codegen=True)
    def subquery(self):
        return models.Subquery(Thing.objects.filter(example=models.OuterRef("pk")).values("number")[:1])

    @subquery.override
    def _(self):
        return self.thing.number


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

    @lookup_property
    def abstract_property(self):
        return models.F("abstract_field")

    class Meta:
        abstract = True


class AnotherAbstract(Abstract):
    another_abstract_field = models.CharField(max_length=256)

    @lookup_property
    def another_abstract_property(self):
        return models.F("another_abstract_field")

    class Meta:
        abstract = True


class Concrete(Abstract):
    concrete_field = models.CharField(max_length=256)


class AnotherConcrete(AnotherAbstract):
    another_concrete_field = models.CharField(max_length=256)
