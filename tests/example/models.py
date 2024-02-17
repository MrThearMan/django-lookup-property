import datetime

from django.db import models
from django.db.models import aggregates, functions
from django.db.models.functions import MD5, Random

from lookup_property import L, lookup_property


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
    def full_name():
        return functions.Concat(
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def name():
        return models.F("full_name")

    @lookup_property
    def f_ref():
        return models.F("first_name")

    @lookup_property
    def combined_expression_add():
        return models.F("age") + 2

    @lookup_property
    def combined_expression_div():
        return models.F("age") / 2

    @lookup_property
    def combined_expression_mod():
        return models.F("age") % 2

    @lookup_property
    def combined_expression_mult():
        return models.F("age") * 2

    @lookup_property
    def combined_expression_pow():
        return models.F("age") ** 2

    @lookup_property
    def combined_expression_sub():
        return models.F("age") - 2

    @lookup_property
    def expression_wrapper():
        return models.ExpressionWrapper(
            models.F("first_name") * 2,
            output_field=models.CharField(),
        )

    @lookup_property(joins=["question"])
    def forward_one_to_one():
        return models.F("question__pk")

    @lookup_property(joins=["thing"])
    def reverse_one_to_one():
        return models.F("thing__pk")

    @lookup_property(joins=["other"])
    def forward_many_to_one():
        return models.F("other__pk")

    @lookup_property(joins=["totals"], skip_codegen=True)
    def reverse_one_to_many():
        return models.F("totals__pk")

    @reverse_one_to_many.override
    def _(self):
        return self.totals.values_list("pk", flat=True).first()

    @lookup_property(joins=["children"], skip_codegen=True)
    def forward_many_to_many():
        return models.F("children__pk")

    @forward_many_to_many.override
    def _(self):
        return self.children.values_list("pk", flat=True).first()

    @lookup_property(joins=["parts"], skip_codegen=True)
    def reverse_many_to_many():
        return models.F("parts__pk")

    @reverse_many_to_many.override
    def _(self):
        return self.parts.values_list("pk", flat=True).first()

    @lookup_property(joins=["thing"])
    def double_join():
        return models.F("thing__far__pk")

    @lookup_property
    def now():
        return functions.Now()

    @lookup_property
    def trunc():
        return functions.Trunc("timestamp", "year")

    @lookup_property
    def trunc_year():
        return functions.TruncYear("timestamp")

    @lookup_property
    def trunc_month():
        return functions.TruncMonth("timestamp")

    @lookup_property
    def trunc_day():
        return functions.TruncDay("timestamp")

    @lookup_property
    def trunc_hour():
        return functions.TruncHour("timestamp")

    @lookup_property
    def trunc_minute():
        return functions.TruncMinute("timestamp")

    @lookup_property
    def trunc_second():
        return functions.TruncSecond("timestamp")

    @lookup_property
    def trunc_week():
        return functions.TruncWeek("timestamp")

    @lookup_property
    def trunc_quarter():
        return functions.TruncQuarter("timestamp")

    @lookup_property
    def trunc_date():
        return functions.TruncDate("timestamp")

    @lookup_property
    def trunc_time():
        return functions.TruncTime("timestamp")

    @lookup_property
    def upper():
        return functions.Upper("first_name")

    @lookup_property
    def lower():
        return functions.Lower("first_name")

    @lookup_property
    def lpad():
        return functions.LPad("first_name", length=20, fill_text=models.Value("."))

    @lookup_property
    def rpad():
        return functions.RPad("first_name", length=20, fill_text=models.Value("."))

    @lookup_property
    def rtrim():
        return functions.RTrim("first_name")

    @lookup_property
    def ltrim():
        return functions.LTrim("first_name")

    @lookup_property
    def length():
        return functions.Length("first_name")

    @lookup_property
    def concat():
        return functions.Concat(
            models.F("first_name"),
            models.Value(" "),
            models.F("last_name"),
            output_field=models.CharField(),
        )

    @lookup_property
    def left():
        return functions.Left("first_name", length=1)

    @lookup_property
    def right():
        return functions.Right("first_name", length=1)

    @lookup_property
    def repeat():
        return functions.Repeat("first_name", number=3)

    @lookup_property
    def repeat():
        return functions.Repeat("first_name", number=3)

    @lookup_property
    def replace():
        return functions.Replace("first_name", text=models.Value("oo"), replacement=models.Value("uu"))

    @lookup_property
    def reverse():
        return functions.Reverse("first_name")

    @lookup_property
    def strindex():
        return functions.StrIndex("first_name", models.Value("o"))

    @lookup_property
    def substr():
        return functions.Substr("first_name", 2)

    @lookup_property
    def substr_length():
        return functions.Substr("first_name", 2, 1)

    @lookup_property
    def trim():
        return functions.Trim("first_name")

    @lookup_property
    def chr_():
        return functions.Chr(65, output_field=models.CharField())

    @lookup_property
    def ord_():
        return functions.Ord("first_name", output_field=models.IntegerField())

    @lookup_property
    def md5():
        return MD5("first_name")

    @lookup_property
    def sha1():
        return functions.SHA1("first_name")

    @lookup_property
    def sha224():
        return functions.SHA224("first_name")

    @lookup_property
    def sha256():
        return functions.SHA256("first_name")

    @lookup_property
    def sha384():
        return functions.SHA384("first_name")

    @lookup_property
    def sha512():
        return functions.SHA512("first_name")

    @lookup_property
    def case():
        return models.Case(
            models.When(
                models.Q(first_name="foo"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def case_2():
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
    def case_3():
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
    def case_4():
        return models.Case(
            models.When(
                condition=models.Q(first_name="foo") & models.Q(last_name="bar"),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property(skip_codegen=True)
    def case_5():
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
    def case_6():
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
    def case_7():
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
    def case_8():
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

    @lookup_property(skip_codegen=True)
    def reffed_by_another_lookup():
        return models.F("parts__far__number")

    @reffed_by_another_lookup.override
    def _(self):
        return self.parts.values_list("far__number", flat=True).first()

    @lookup_property
    def refs_another_lookup():
        return models.Case(
            models.When(
                models.Q(L(reffed_by_another_lookup=1)),
                then=models.Value("foo"),
            ),
            default=models.Value("bar"),
            output_field=models.CharField(),
        )

    @lookup_property
    def cast_str():
        return functions.Cast("age", output_field=models.CharField())

    @lookup_property
    def cast_int():
        return functions.Cast("age", output_field=models.IntegerField())

    @lookup_property
    def cast_float():
        return functions.Cast("age", output_field=models.FloatField())

    @lookup_property
    def cast_decimal():
        return functions.Cast("age", output_field=models.DecimalField())

    @lookup_property
    def cast_bool():
        return functions.Cast("age", output_field=models.BooleanField())

    @lookup_property
    def cast_uuid():
        return functions.Cast(
            models.Value("a2cabdde-bc6b-4626-87fe-dea41458dd8f"),
            output_field=models.UUIDField(),
        )

    @lookup_property
    def cast_json():
        return functions.Cast(models.Value('{"foo": 1}'), output_field=models.JSONField())

    # TODO: Collate

    @lookup_property
    def coalesce():
        return functions.Coalesce("first_name", "last_name")

    @lookup_property
    def coalesce_2():
        return functions.Coalesce(functions.Concat("first_name", "last_name"), models.Value("."))

    @lookup_property
    def greatest():
        return functions.Greatest("age", "number")

    @lookup_property
    def least():
        return functions.Least("age", "number")

    @lookup_property
    def json_object():
        return functions.JSONObject(
            name=functions.Upper("name"),
            alias=models.Value("alias"),
            age=models.F("age") * 2,
        )

    @lookup_property
    def nullif():
        return functions.NullIf("first_name", "last_name")

    @lookup_property
    def extract():
        return functions.Extract("timestamp", "year")

    @lookup_property
    def extract_year():
        return functions.ExtractYear("timestamp")

    @lookup_property
    def extract_iso_year():
        return functions.ExtractIsoYear("timestamp")

    @lookup_property
    def extract_month():
        return functions.ExtractMonth("timestamp")

    @lookup_property
    def extract_day():
        return functions.ExtractDay("timestamp")

    @lookup_property
    def extract_week():
        return functions.ExtractWeek("timestamp")

    @lookup_property
    def extract_weekday():
        return functions.ExtractWeekDay("timestamp")

    @lookup_property
    def extract_iso_weekday():
        return functions.ExtractIsoWeekDay("timestamp")

    @lookup_property
    def extract_quarter():
        return functions.ExtractQuarter("timestamp")

    @lookup_property
    def extract_hour():
        return functions.ExtractHour("timestamp")

    @lookup_property
    def extract_minute():
        return functions.ExtractMinute("timestamp")

    @lookup_property
    def extract_second():
        return functions.ExtractSecond("timestamp")

    @lookup_property
    def abs_():
        return functions.Abs("number")

    @lookup_property
    def acos():
        return functions.ACos("number")

    @lookup_property
    def asin():
        return functions.ASin("number")

    @lookup_property
    def atan():
        return functions.ATan("number")

    @lookup_property
    def atan2():
        return functions.ATan2("number", 2)

    @lookup_property
    def ceil():
        return functions.Ceil("number")

    @lookup_property
    def cos():
        return functions.Cos("number")

    @lookup_property
    def cot():
        return functions.Cot("number")

    @lookup_property
    def degrees():
        return functions.Degrees("number")

    @lookup_property
    def exp():
        return functions.Exp("number")

    @lookup_property
    def floor():
        return functions.Floor("number")

    @lookup_property
    def ln():
        return functions.Ln("number")

    @lookup_property
    def log():
        return functions.Log("number", 10)

    @lookup_property
    def mod():
        return functions.Mod("number", 4)

    @lookup_property
    def pi():
        return functions.Pi()

    @lookup_property
    def power():
        return functions.Power("number", 3)

    @lookup_property
    def radians():
        return functions.Radians("number")

    @lookup_property
    def random():
        return Random()

    @lookup_property
    def round_():
        return functions.Round("number")

    @lookup_property
    def round_2():
        return functions.Round("number", precision=2)

    @lookup_property
    def sign():
        return functions.Sign("number")

    @lookup_property
    def sin():
        return functions.Sin("number")

    @lookup_property
    def sqrt():
        return functions.Sqrt("number")

    @lookup_property
    def tan():
        return functions.Tan("number")

    @lookup_property
    def q():
        return models.Q(first_name="foo")

    @lookup_property
    def q_rel():
        return models.Q(thing__name="foo")

    @lookup_property
    def q_neg():
        return ~models.Q(first_name="foo")

    @lookup_property
    def q_empty():
        return models.Q()

    @lookup_property
    def q_exact():
        return models.Q(first_name__exact="foo")

    @lookup_property
    def q_iexact():
        return models.Q(first_name__iexact="FOO")

    @lookup_property
    def q_iexact_null():
        return models.Q(first_name__iexact=None)

    @lookup_property
    def q_gte():
        return models.Q(timestamp__gte=functions.Now())

    @lookup_property
    def q_gt():
        return models.Q(timestamp__gt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))

    @lookup_property
    def q_lte():
        return models.Q(timestamp__lte=functions.Now())

    @lookup_property
    def q_lt():
        return models.Q(timestamp__lt=datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC))

    @lookup_property
    def q_in_list():
        return models.Q(first_name__in=["foo", "bar"])

    @lookup_property
    def q_in_tuple():
        return models.Q(first_name__in=("foo", "bar"))

    @lookup_property
    def q_in_set():
        return models.Q(first_name__in={"foo", "bar"})

    @lookup_property
    def q_in_dict():
        return models.Q(first_name__in={"foo": "bar"})

    @lookup_property
    def q_contains():
        return models.Q(first_name__contains="fo")

    @lookup_property
    def q_icontains():
        return models.Q(first_name__icontains="FO")

    @lookup_property
    def q_startswith():
        return models.Q(first_name__startswith="fo")

    @lookup_property
    def q_istartswith():
        return models.Q(first_name__istartswith="FO")

    @lookup_property
    def q_endswith():
        return models.Q(first_name__endswith="fo")

    @lookup_property
    def q_iendswith():
        return models.Q(first_name__iendswith="FO")

    @lookup_property
    def q_range():
        return models.Q(
            timestamp__range=(
                datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC),
                datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC),
            ),
        )

    @lookup_property
    def q_isnull():
        return models.Q(first_name__isnull=True)

    @lookup_property
    def q_regex():
        return models.Q(first_name__regex=r"[a-z]*")

    @lookup_property
    def q_iregex():
        return models.Q(first_name__iregex=r"[A-Z]*")

    @lookup_property
    def q_or():
        return models.Q(first_name="foo") | models.Q(last_name="bar")

    @lookup_property
    def q_and():
        return models.Q(first_name="foo") & models.Q(last_name="bar")

    @lookup_property
    def q_xor():
        return models.Q(first_name="foo") ^ models.Q(last_name="bar")

    @lookup_property
    def count_field():
        return aggregates.Count("*")

    @lookup_property
    def count_field_filter():
        return aggregates.Count("pk", filter=models.Q(number__lte=10))

    @lookup_property
    def count_rel():
        return aggregates.Count("totals__pk")

    @lookup_property(joins=["parts"])
    def count_rel_deep():
        return aggregates.Count("parts__aliens")

    @lookup_property
    def count_rel_filter():
        return aggregates.Count("totals", filter=models.Q(totals__name__contains="bar"))

    @lookup_property
    def max_():
        return aggregates.Max("number")

    @lookup_property
    def max_rel():
        return aggregates.Max("totals__number")

    @lookup_property
    def min_():
        return aggregates.Min("number")

    @lookup_property
    def min_rel():
        return aggregates.Min("totals__number")

    @lookup_property
    def sum_():
        return aggregates.Sum("number")

    @lookup_property
    def sum_rel():
        return aggregates.Sum("totals__number")

    @lookup_property
    def sum_filter():
        return aggregates.Sum("number", filter=models.Q(number__lte=3))

    @lookup_property
    def avg():
        return aggregates.Avg("number")

    @lookup_property
    def std_dev():
        return aggregates.StdDev("number")

    @lookup_property
    def variance():
        return aggregates.Variance("number")

    @lookup_property(skip_codegen=True)
    def subquery():
        return models.Subquery(Thing.objects.filter(example=models.OuterRef("pk")).values("number")[:1])

    @subquery.override
    def _(self):
        return self.thing.number

    @lookup_property(skip_codegen=True)
    def exists():
        return models.Exists(Total.objects.filter(example=models.OuterRef("pk"), number=1))

    @exists.override
    def _(self):
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
    def abstract_property():
        return models.F("abstract_field")

    class Meta:
        abstract = True


class AnotherAbstract(Abstract):
    another_abstract_field = models.CharField(max_length=256)

    @lookup_property
    def another_abstract_property():
        return models.F("another_abstract_field")

    class Meta:
        abstract = True


class Concrete(Abstract):
    concrete_field = models.CharField(max_length=256)


class AnotherConcrete(AnotherAbstract):
    another_concrete_field = models.CharField(max_length=256)
