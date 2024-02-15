from inspect import cleandoc

from tests.example.models import Example


def test_lookup_property__f_ref__source():
    assert Example.f_ref.func_source == cleandoc(
        """
        def f_ref(self):
            return self.first_name
        """,
    )


def test_lookup_property__combined_expression_add__source():
    assert Example.combined_expression_add.func_source == cleandoc(
        """
        def combined_expression_add(self):
            return self.age + 2
        """,
    )


def test_lookup_property__combined_expression_div__source():
    assert Example.combined_expression_div.func_source == cleandoc(
        """
        def combined_expression_div(self):
            return self.age / 2
        """,
    )


def test_lookup_property__combined_expression_mod__source():
    assert Example.combined_expression_mod.func_source == cleandoc(
        """
        def combined_expression_mod(self):
            return self.age % 2
        """,
    )


def test_lookup_property__combined_expression_mult__source():
    assert Example.combined_expression_mult.func_source == cleandoc(
        """
        def combined_expression_mult(self):
            return self.age * 2
        """,
    )


def test_lookup_property__combined_expression_pow__source():
    assert Example.combined_expression_pow.func_source == cleandoc(
        """
        def combined_expression_pow(self):
            return self.age ** 2
        """,
    )


def test_lookup_property__combined_expression_sub__source():
    assert Example.combined_expression_sub.func_source == cleandoc(
        """
        def combined_expression_sub(self):
            return self.age - 2
        """,
    )


def test_lookup_property__expression_wrapper__source():
    assert Example.expression_wrapper.func_source == cleandoc(
        """
        def expression_wrapper(self):
            return str(self.first_name * 2)
        """,
    )


def test_lookup_property__forward_one_to_one__source():
    assert Example.forward_one_to_one.func_source == cleandoc(
        """
        def forward_one_to_one(self):
            return self.question.pk
        """,
    )


def test_lookup_property__reverse_one_to_one__source():
    assert Example.reverse_one_to_one.func_source == cleandoc(
        """
        def reverse_one_to_one(self):
            return self.thing.pk
        """,
    )


def test_lookup_property__forward_many_to_one__source():
    assert Example.forward_many_to_one.func_source == cleandoc(
        """
        def forward_many_to_one(self):
            return self.other.pk
        """,
    )


def test_lookup_property__reverse_one_to_many__source():
    assert Example.reverse_one_to_many.func_source == cleandoc(
        """
        @reverse_one_to_many.override
        def _(self):
            return self.totals.values_list('pk', flat=True).first()
        """,
    )


def test_lookup_property__forward_many_to_many__source():
    assert Example.forward_many_to_many.func_source == cleandoc(
        """
        @forward_many_to_many.override
        def _(self):
            return self.children.values_list('pk', flat=True).first()
        """,
    )


def test_lookup_property__reverse_many_to_many__source():
    assert Example.reverse_many_to_many.func_source == cleandoc(
        """
        @reverse_many_to_many.override
        def _(self):
            return self.parts.values_list('pk', flat=True).first()
        """,
    )


def test_lookup_property__double_join__source():
    assert Example.double_join.func_source == cleandoc(
        """
        def double_join(self):
            return self.thing.far.pk
        """,
    )


def test_lookup_property__q__source():
    assert Example.q.func_source == cleandoc(
        """
        def q(self):
            return self.first_name == 'foo'
        """,
    )


def test_lookup_property__q_neg__source():
    assert Example.q_neg.func_source == cleandoc(
        """
        def q_neg(self):
            return not self.first_name == 'foo'
        """,
    )


def test_lookup_property__q_empty__source():
    assert Example.q_empty.func_source == cleandoc(
        """
        def q_empty(self):
            return True
        """,
    )


def test_lookup_property__q_exact__source():
    assert Example.q_exact.func_source == cleandoc(
        """
        def q_exact(self):
            return self.first_name == 'foo'
        """,
    )


def test_lookup_property__q_gte__source():
    assert Example.q_gte.func_source == cleandoc(
        """
        def q_gte(self):
            import datetime
            return self.timestamp >= datetime.datetime.now(tz=datetime.timezone.utc)
        """,
    )


def test_lookup_property__q_gt__source():
    assert Example.q_gt.func_source == cleandoc(
        """
        def q_gt(self, arg0):
            return self.timestamp > arg0()
        """,
    )


def test_lookup_property__q_lte__source():
    assert Example.q_lte.func_source == cleandoc(
        """
        def q_lte(self):
            import datetime
            return self.timestamp <= datetime.datetime.now(tz=datetime.timezone.utc)
        """,
    )


def test_lookup_property__q_lt__source():
    assert Example.q_lt.func_source == cleandoc(
        """
        def q_lt(self, arg1):
            return self.timestamp < arg1()
        """,
    )


def test_lookup_property__q_in_list__source():
    assert Example.q_in_list.func_source == cleandoc(
        """
        def q_in_list(self):
            return self.first_name in ['foo', 'bar']
        """,
    )


def test_lookup_property__q_in_tuple__source():
    assert Example.q_in_tuple.func_source == cleandoc(
        """
        def q_in_tuple(self):
            return self.first_name in ('foo', 'bar')
        """,
    )


def test_lookup_property__q_in_set__source():
    assert Example.q_in_set.func_source in (
        cleandoc(
            """
            def q_in_set(self):
                return self.first_name in {'foo', 'bar'}
            """,
        ),
        cleandoc(
            """
            def q_in_set(self):
                return self.first_name in {'bar', 'foo'}
            """,
        ),
    )


def test_lookup_property__q_in_dict__source():
    assert Example.q_in_dict.func_source == cleandoc(
        """
        def q_in_dict(self):
            return self.first_name in {'foo': 'bar'}
        """,
    )


def test_lookup_property__q_contains__source():
    assert Example.q_contains.func_source == cleandoc(
        """
        def q_contains(self):
            return 'fo' in self.first_name
        """,
    )


def test_lookup_property__q_icontains__source():
    assert Example.q_icontains.func_source == cleandoc(
        """
        def q_icontains(self):
            return 'FO'.casefold() in self.first_name.casefold()
        """,
    )


def test_lookup_property__q_startswith__source():
    assert Example.q_startswith.func_source == cleandoc(
        """
        def q_startswith(self):
            return self.first_name.startswith('fo')
        """,
    )


def test_lookup_property__q_istartswith__source():
    assert Example.q_istartswith.func_source == cleandoc(
        """
        def q_istartswith(self):
            return self.first_name.casefold().startswith('FO'.casefold())
        """,
    )


def test_lookup_property__q_endswith__source():
    assert Example.q_endswith.func_source == cleandoc(
        """
        def q_endswith(self):
            return self.first_name.endswith('fo')
        """,
    )


def test_lookup_property__q_iendswith__source():
    assert Example.q_iendswith.func_source == cleandoc(
        """
        def q_iendswith(self):
            return self.first_name.casefold().endswith('FO'.casefold())
        """,
    )


def test_lookup_property__q_range__source():
    assert Example.q_range.func_source == cleandoc(
        """
        def q_range(self, arg2, arg3):
            return arg2() < self.timestamp < arg3()
        """,
    )


def test_lookup_property__q_isnull__source():
    assert Example.q_isnull.func_source == cleandoc(
        """
        def q_isnull(self):
            return self.first_name is None
        """,
    )


def test_lookup_property__q_regex__source():
    assert Example.q_regex.func_source == cleandoc(
        """
        def q_regex(self):
            import re
            return re.match('[a-z]*', self.first_name) is not None
        """,
    )


def test_lookup_property__q_iregex__source():
    assert Example.q_iregex.func_source == cleandoc(
        """
        def q_iregex(self):
            import re
            return re.match('[A-Z]*', self.first_name.casefold()) is not None
        """,
    )


def test_lookup_property__q_or__source():
    assert Example.q_or.func_source == cleandoc(
        """
        def q_or(self):
            return self.first_name == 'foo' or self.last_name == 'bar'
        """,
    )


def test_lookup_property__q_and__source():
    assert Example.q_and.func_source == cleandoc(
        """
        def q_and(self):
            return self.first_name == 'foo' and self.last_name == 'bar'
        """,
    )


def test_lookup_property__q_xor__source():
    assert Example.q_xor.func_source == cleandoc(
        """
        def q_xor(self):
            return (self.first_name == 'foo') ^ (self.last_name == 'bar')
        """,
    )


def test_lookup_property__now__source():
    assert Example.now.func_source == cleandoc(
        """
        def now(self):
            import datetime
            return datetime.datetime.now(tz=datetime.timezone.utc)
        """,
    )


def test_lookup_property__trunc_year__source():
    assert Example.trunc_year.func_source == cleandoc(
        """
        def trunc_year(self):
            return self.timestamp.year
        """,
    )


def test_lookup_property__trunc_month__source():
    assert Example.trunc_month.func_source == cleandoc(
        """
        def trunc_month(self):
            return self.timestamp.month
        """,
    )


def test_lookup_property__trunc_day__source():
    assert Example.trunc_day.func_source == cleandoc(
        """
        def trunc_day(self):
            return self.timestamp.day
        """,
    )


def test_lookup_property__trunc_hour__source():
    assert Example.trunc_hour.func_source == cleandoc(
        """
        def trunc_hour(self):
            return self.timestamp.hour
        """,
    )


def test_lookup_property__trunc_minute__source():
    assert Example.trunc_minute.func_source == cleandoc(
        """
        def trunc_minute(self):
            return self.timestamp.minute
        """,
    )


def test_lookup_property__trunc_second__source():
    assert Example.trunc_second.func_source == cleandoc(
        """
        def trunc_second(self):
            return self.timestamp.second
        """,
    )


def test_lookup_property__trunc_week__source():
    x = "self.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)"
    y = "datetime.timedelta(days=self.timestamp.weekday())"
    assert Example.trunc_week.func_source == cleandoc(
        f"""
        def trunc_week(self):
            import datetime
            return {x} - {y}
        """,
    )


def test_lookup_property__trunc_quarter__source():
    month = "(self.timestamp.month + 2) // 3"
    assert Example.trunc_quarter.func_source == cleandoc(
        f"""
        def trunc_quarter(self):
            import datetime
            return self.timestamp.replace(month={month}, day=1, hour=0, minute=0, second=0, microsecond=0)
        """,
    )


def test_lookup_property__trunc_date__source():
    assert Example.trunc_date.func_source == cleandoc(
        """
        def trunc_date(self):
            return self.timestamp.date()
        """,
    )


def test_lookup_property__trunc_time__source():
    assert Example.trunc_time.func_source == cleandoc(
        """
        def trunc_time(self):
            return self.timestamp.timetz()
        """,
    )


def test_lookup_property__upper__source():
    assert Example.upper.func_source == cleandoc(
        """
        def upper(self):
            return self.first_name.upper()
        """,
    )


def test_lookup_property__lower__source():
    assert Example.lower.func_source == cleandoc(
        """
        def lower(self):
            return self.first_name.lower()
        """,
    )


def test_lookup_property__lpad__source():
    assert Example.lpad.func_source == cleandoc(
        """
        def lpad(self):
            return self.first_name.rjust(20, '.')
        """,
    )


def test_lookup_property__rpad__source():
    assert Example.rpad.func_source == cleandoc(
        """
        def rpad(self):
            return self.first_name.ljust(20, '.')
        """,
    )


def test_lookup_property__rtrim__source():
    assert Example.rtrim.func_source == cleandoc(
        """
        def rtrim(self):
            return self.first_name.rstrip()
        """,
    )


def test_lookup_property__ltrim__source():
    assert Example.ltrim.func_source == cleandoc(
        """
        def ltrim(self):
            return self.first_name.lstrip()
        """,
    )


def test_lookup_property__length__source():
    assert Example.length.func_source == cleandoc(
        """
        def length(self):
            return len(self.first_name)
        """,
    )


def test_lookup_property__concat__source():
    assert Example.concat.func_source == cleandoc(
        """
        def concat(self):
            return self.first_name + (' ' + self.last_name)
        """,
    )


def test_lookup_property__left__source():
    assert Example.left.func_source == cleandoc(
        """
        def left(self):
            return self.first_name[:1]
        """,
    )


def test_lookup_property__right__source():
    assert Example.right.func_source == cleandoc(
        """
        def right(self):
            return self.first_name[-1:]
        """,
    )


def test_lookup_property__repeat__source():
    assert Example.repeat.func_source == cleandoc(
        """
        def repeat(self):
            return self.first_name * 3
        """,
    )


def test_lookup_property__replace__source():
    assert Example.replace.func_source == cleandoc(
        """
        def replace(self):
            return self.first_name.replace('oo', 'uu')
        """,
    )


def test_lookup_property__reverse__source():
    assert Example.reverse.func_source == cleandoc(
        """
        def reverse(self):
            return self.first_name[::-1]
        """,
    )


def test_lookup_property__strindex__source():
    assert Example.strindex.func_source == cleandoc(
        """
        def strindex(self):
            if 'o' in self.first_name:
                return self.first_name.index('o') + 1
            else:
                return 0
        """,
    )


def test_lookup_property__substr__source():
    assert Example.substr.func_source == cleandoc(
        """
        def substr(self):
            return self.first_name[2 - 1:]
        """,
    )


def test_lookup_property__substr_length__source():
    assert Example.substr_length.func_source == cleandoc(
        """
        def substr_length(self):
            return self.first_name[2 - 1:2 + 1 - 1]
        """,
    )


def test_lookup_property__trim__source():
    assert Example.trim.func_source == cleandoc(
        """
        def trim(self):
            return self.first_name.strip()
        """,
    )


def test_lookup_property__chr__source():
    assert Example.chr_.func_source == cleandoc(
        """
        def chr_(self):
            return chr(65)
        """,
    )


def test_lookup_property__ord__source():
    assert Example.ord_.func_source == cleandoc(
        """
        def ord_(self):
            return ord(self.first_name[0])
        """,
    )


def test_lookup_property__md5__source():
    assert Example.md5.func_source == cleandoc(
        """
        def md5(self):
            import hashlib
            return hashlib.md5(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__sha1__source():
    assert Example.sha1.func_source == cleandoc(
        """
        def sha1(self):
            import hashlib
            return hashlib.sha1(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__sha224__source():
    assert Example.sha224.func_source == cleandoc(
        """
        def sha224(self):
            import hashlib
            return hashlib.sha224(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__sha256__source():
    assert Example.sha256.func_source == cleandoc(
        """
        def sha256(self):
            import hashlib
            return hashlib.sha256(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__sha384__source():
    assert Example.sha384.func_source == cleandoc(
        """
        def sha384(self):
            import hashlib
            return hashlib.sha384(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__sha512__source():
    assert Example.sha512.func_source == cleandoc(
        """
        def sha512(self):
            import hashlib
            return hashlib.sha512(self.first_name.encode()).hexdigest()
        """,
    )


def test_lookup_property__case__source():
    assert Example.case.func_source == cleandoc(
        """
        def case(self):
            return 'foo' if self.first_name == 'foo' else 'bar'
        """,
    )


def test_lookup_property__case_2__source():
    assert Example.case_2.func_source == cleandoc(
        """
        def case_2(self):
            return 'foo' if self.first_name == 'fizz' else 'bar' if self.last_name == 'bar' else 'baz'
        """,
    )


def test_lookup_property__case_3__source():
    cond_1 = "('fizz' if self.last_name == 'bar' else 'buzz')"
    assert Example.case_3.func_source == cleandoc(
        f"""
        def case_3(self):
            return {cond_1} if self.first_name == 'foo' else 'foo' if self.last_name == 'bar' else 'bar'
        """,
    )


def test_lookup_property__case_4__source():
    assert Example.case_4.func_source == cleandoc(
        """
        def case_4(self):
            return 'foo' if self.first_name == 'foo' and self.last_name == 'bar' else 'bar'
        """,
    )


def test_lookup_property__case_5__source():
    assert Example.case_5.func_source == cleandoc(
        """
        @case_5.override
        def _(self):
            return 'foo' if self.totals.filter(number=1).exists() else 'bar'
        """,
    )


def test_lookup_property__case_6__source():
    assert Example.case_6.func_source == cleandoc(
        """
        @case_6.override
        def _(self):
            return 'foo' if self.parts.filter(far__number=1).exists() else 'bar'
        """,
    )


def test_lookup_property__case_7__source():
    assert Example.case_7.func_source == cleandoc(
        """
        @case_7.override
        def _(self):
            return 'foo' if self.parts.filter(number=1, far__number=1).exists() else 'bar'
        """,
    )


def test_lookup_property__cast_str__source():
    assert Example.cast_str.func_source == cleandoc(
        """
        def cast_str(self):
            return str(self.age)
        """,
    )


def test_lookup_property__cast_int__source():
    assert Example.cast_int.func_source == cleandoc(
        """
        def cast_int(self):
            return int(self.age)
        """,
    )


def test_lookup_property__cast_float__source():
    assert Example.cast_float.func_source == cleandoc(
        """
        def cast_float(self):
            return float(self.age)
        """,
    )


def test_lookup_property__cast_decimal__source():
    assert Example.cast_decimal.func_source == cleandoc(
        """
        def cast_decimal(self):
            import decimal
            return decimal.Decimal(self.age)
        """,
    )


def test_lookup_property__cast_bool__source():
    assert Example.cast_bool.func_source == cleandoc(
        """
        def cast_bool(self):
            return bool(self.age)
        """,
    )


def test_lookup_property__cast_uuid__source():
    assert Example.cast_uuid.func_source == cleandoc(
        """
        def cast_uuid(self):
            import uuid
            return uuid.UUID('a2cabdde-bc6b-4626-87fe-dea41458dd8f')
        """,
    )


def test_lookup_property__cast_json__source():
    assert Example.cast_json.func_source == cleandoc(
        """
        def cast_json(self):
            import json
            return json.loads('{"foo": 1}')
        """,
    )


def test_lookup_property__coalesce__source():
    cond_1 = "self.first_name if self.first_name is not None"
    assert Example.coalesce.func_source == cleandoc(
        f"""
        def coalesce(self):
            return {cond_1} else self.last_name if self.last_name is not None else None
        """,
    )


def test_lookup_property__coalesce_2__source():
    full_name = "self.first_name + self.last_name"
    assert Example.coalesce_2.func_source == cleandoc(
        f"""
        def coalesce_2(self):
            return {full_name} if {full_name} is not None else '.' if '.' is not None else None
        """,
    )


def test_lookup_property__greatest__source():
    assert Example.greatest.func_source == cleandoc(
        """
        def greatest(self):
            return max({self.age, self.number}.difference({None}), default=None)
        """,
    )


def test_lookup_property__least__source():
    assert Example.least.func_source == cleandoc(
        """
        def least(self):
            return min({self.age, self.number}.difference({None}), default=None)
        """,
    )


def test_lookup_property__json_object__source():
    assert Example.json_object.func_source == cleandoc(
        """
        def json_object(self):
            return {'name': self.name.upper(), 'alias': 'alias', 'age': self.age * 2}
        """,
    )


def test_lookup_property__nullif__source():
    assert Example.nullif.func_source == cleandoc(
        """
        def nullif(self):
            return None if self.first_name == self.last_name else self.first_name
        """,
    )


def test_lookup_property__extract_year__source():
    assert Example.extract_year.func_source == cleandoc(
        """
        def extract_year(self):
            return self.timestamp.year
        """,
    )


def test_lookup_property__extract_month__source():
    assert Example.extract_month.func_source == cleandoc(
        """
        def extract_month(self):
            return self.timestamp.month
        """,
    )


def test_lookup_property__extract_day__source():
    assert Example.extract_day.func_source == cleandoc(
        """
        def extract_day(self):
            return self.timestamp.day
        """,
    )


def test_lookup_property__extract_hour__source():
    assert Example.extract_hour.func_source == cleandoc(
        """
        def extract_hour(self):
            return self.timestamp.hour
        """,
    )


def test_lookup_property__extract_minute__source():
    assert Example.extract_minute.func_source == cleandoc(
        """
        def extract_minute(self):
            return self.timestamp.minute
        """,
    )


def test_lookup_property__extract_second__source():
    assert Example.extract_second.func_source == cleandoc(
        """
        def extract_second(self):
            return self.timestamp.second
        """,
    )


def test_lookup_property__extract_quarter__source():
    month = "(self.timestamp.month + 2) // 3"
    assert Example.extract_quarter.func_source == cleandoc(
        f"""
        def extract_quarter(self):
            import datetime
            return self.timestamp.replace(month={month}, day=1, hour=0, minute=0, second=0, microsecond=0)
        """,
    )


def test_lookup_property__extract_iso_year__source():
    assert Example.extract_iso_year.func_source == cleandoc(
        """
        def extract_iso_year(self):
            return self.timestamp.isocalendar().year
        """,
    )


def test_lookup_property__extract_week__source():
    assert Example.extract_week.func_source == cleandoc(
        """
        def extract_week(self):
            return self.timestamp.isocalendar().week
        """,
    )


def test_lookup_property__extract_iso_weekday__source():
    assert Example.extract_iso_weekday.func_source == cleandoc(
        """
        def extract_iso_weekday(self):
            return self.timestamp.isocalendar().weekday
        """,
    )


def test_lookup_property__abs__source():
    assert Example.abs_.func_source == cleandoc(
        """
        def abs_(self):
            return abs(self.number)
        """,
    )


def test_lookup_property__acos__source():
    assert Example.acos.func_source == cleandoc(
        """
        def acos(self):
            import math
            return math.acos(self.number)
        """,
    )


def test_lookup_property__asin__source():
    assert Example.asin.func_source == cleandoc(
        """
        def asin(self):
            import math
            return math.asin(self.number)
        """,
    )


def test_lookup_property__atan__source():
    assert Example.atan.func_source == cleandoc(
        """
        def atan(self):
            import math
            return math.atan(self.number)
        """,
    )


def test_lookup_property__atan2__source():
    assert Example.atan2.func_source == cleandoc(
        """
        def atan2(self):
            import math
            return math.atan2(self.number, 2)
        """,
    )


def test_lookup_property__ceil__source():
    assert Example.ceil.func_source == cleandoc(
        """
        def ceil(self):
            import math
            return math.ceil(self.number)
        """,
    )


def test_lookup_property__cos__source():
    assert Example.cos.func_source == cleandoc(
        """
        def cos(self):
            import math
            return math.cos(self.number)
        """,
    )


def test_lookup_property__cot__source():
    assert Example.cot.func_source == cleandoc(
        """
        def cot(self):
            import math
            return 1 / math.tan(self.number)
        """,
    )


def test_lookup_property__degrees__source():
    assert Example.degrees.func_source == cleandoc(
        """
        def degrees(self):
            import math
            return math.degrees(self.number)
        """,
    )


def test_lookup_property__exp__source():
    assert Example.exp.func_source == cleandoc(
        """
        def exp(self):
            import math
            return math.exp(self.number)
        """,
    )


def test_lookup_property__floor__source():
    assert Example.floor.func_source == cleandoc(
        """
        def floor(self):
            import math
            return math.floor(self.number)
        """,
    )


def test_lookup_property__ln__source():
    assert Example.ln.func_source == cleandoc(
        """
        def ln(self):
            import math
            return math.log(self.number)
        """,
    )


def test_lookup_property__log__source():
    assert Example.log.func_source == cleandoc(
        """
        def log(self):
            import math
            return math.log(self.number, 10)
        """,
    )


def test_lookup_property__mod__source():
    assert Example.mod.func_source == cleandoc(
        """
        def mod(self):
            return self.number % 4
        """,
    )


def test_lookup_property__pi__source():
    assert Example.pi.func_source == cleandoc(
        """
        def pi(self):
            import math
            return math.pi
        """,
    )


def test_lookup_property__power__source():
    assert Example.power.func_source == cleandoc(
        """
        def power(self):
            import math
            return math.pow(self.number, 3)
        """,
    )


def test_lookup_property__radians__source():
    assert Example.radians.func_source == cleandoc(
        """
        def radians(self):
            import math
            return math.radians(self.number)
        """,
    )


def test_lookup_property__random__source():
    assert Example.random.func_source == cleandoc(
        """
        def random(self):
            import random
            return random.random()
        """,
    )


def test_lookup_property__round__source():
    assert Example.round_.func_source == cleandoc(
        """
        def round_(self):
            return round(self.number, 0)
        """,
    )


def test_lookup_property__round_2__source():
    assert Example.round_2.func_source == cleandoc(
        """
        def round_2(self):
            return round(self.number, 2)
        """,
    )


def test_lookup_property__sign__source():
    assert Example.sign.func_source == cleandoc(
        """
        def sign(self):
            return int(self.number > 0) - int(self.number < 0)
        """,
    )


def test_lookup_property__sin__source():
    assert Example.sin.func_source == cleandoc(
        """
        def sin(self):
            import math
            return math.sin(self.number)
        """,
    )


def test_lookup_property__sqrt__source():
    assert Example.sqrt.func_source == cleandoc(
        """
        def sqrt(self):
            import math
            return math.sqrt(self.number)
        """,
    )


def test_lookup_property__tan__source():
    assert Example.tan.func_source == cleandoc(
        """
        def tan(self):
            import math
            return math.tan(self.number)
        """,
    )


def test_lookup_property__count_field__source():
    assert Example.count_field.func_source == cleandoc(
        """
        def count_field(self, arg4):
            return self.__class__.objects.aggregate(arg4=arg4())['arg4']
        """,
    )


def test_lookup_property__count_field_filter__source():
    assert Example.count_field_filter.func_source == cleandoc(
        """
        def count_field_filter(self, arg5):
            return self.__class__.objects.aggregate(arg5=arg5())['arg5']
        """,
    )


def test_lookup_property__count_rel__source():
    assert Example.count_rel.func_source == cleandoc(
        """
        def count_rel(self, arg6):
            return self.__class__.objects.aggregate(arg6=arg6())['arg6']
        """,
    )


def test_lookup_property__count_rel_deep__source():
    assert Example.count_rel_deep.func_source == cleandoc(
        """
        def count_rel_deep(self, arg7):
            return self.__class__.objects.aggregate(arg7=arg7())['arg7']
        """,
    )


def test_lookup_property__count_rel_filter__source():
    assert Example.count_rel_filter.func_source == cleandoc(
        """
        def count_rel_filter(self, arg8):
            return self.__class__.objects.aggregate(arg8=arg8())['arg8']
        """,
    )


def test_lookup_property__max__source():
    assert Example.max_.func_source == cleandoc(
        """
        def max_(self, arg9):
            return self.__class__.objects.aggregate(arg9=arg9())['arg9']
        """,
    )


def test_lookup_property__max_rel__source():
    assert Example.max_rel.func_source == cleandoc(
        """
        def max_rel(self, arg10):
            return self.__class__.objects.aggregate(arg10=arg10())['arg10']
        """,
    )


def test_lookup_property__min__source():
    assert Example.min_.func_source == cleandoc(
        """
        def min_(self, arg11):
            return self.__class__.objects.aggregate(arg11=arg11())['arg11']
        """,
    )


def test_lookup_property__min_rel__source():
    assert Example.min_rel.func_source == cleandoc(
        """
        def min_rel(self, arg12):
            return self.__class__.objects.aggregate(arg12=arg12())['arg12']
        """,
    )


def test_lookup_property__sum__source():
    assert Example.sum_.func_source == cleandoc(
        """
        def sum_(self, arg13):
            return self.__class__.objects.aggregate(arg13=arg13())['arg13']
        """,
    )


def test_lookup_property__sum_rel__source():
    assert Example.sum_rel.func_source == cleandoc(
        """
        def sum_rel(self, arg14):
            return self.__class__.objects.aggregate(arg14=arg14())['arg14']
        """,
    )


def test_lookup_property__sum_filter__source():
    assert Example.sum_filter.func_source == cleandoc(
        """
        def sum_filter(self, arg15):
            return self.__class__.objects.aggregate(arg15=arg15())['arg15']
        """,
    )


def test_lookup_property__avg__source():
    assert Example.avg.func_source == cleandoc(
        """
        def avg(self, arg16):
            return self.__class__.objects.aggregate(arg16=arg16())['arg16']
        """,
    )


def test_lookup_property__std_dev__source():
    assert Example.std_dev.func_source == cleandoc(
        """
        def std_dev(self, arg17):
            return self.__class__.objects.aggregate(arg17=arg17())['arg17']
        """,
    )


def test_lookup_property__variance__source():
    assert Example.variance.func_source == cleandoc(
        """
        def variance(self, arg18):
            return self.__class__.objects.aggregate(arg18=arg18())['arg18']
        """,
    )


def test_lookup_property__refs_another_lookup__source():
    assert Example.refs_another_lookup.func_source == cleandoc(
        """
        def refs_another_lookup(self):
            return 'foo' if self.reffed_by_another_lookup == 1 else 'bar'
        """,
    )
