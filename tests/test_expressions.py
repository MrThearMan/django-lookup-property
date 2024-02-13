import pytest

from tests.factories import ExampleFactory, TotalFactory, ThingFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__f_ref():
    example = ExampleFactory.create()
    assert example.f_ref == "foo"


def test_lookup_property__combined_expression_add():
    example = ExampleFactory.create()
    assert example.combined_expression_add == 20


def test_lookup_property__combined_expression_div():
    example = ExampleFactory.create()
    assert example.combined_expression_div == 9


def test_lookup_property__combined_expression_mod():
    example = ExampleFactory.create()
    assert example.combined_expression_mod == 0


def test_lookup_property__combined_expression_mult():
    example = ExampleFactory.create()
    assert example.combined_expression_mult == 36


def test_lookup_property__combined_expression_pow():
    example = ExampleFactory.create()
    assert example.combined_expression_pow == 324


def test_lookup_property__combined_expression_sub():
    example = ExampleFactory.create()
    assert example.combined_expression_sub == 16


def test_lookup_property__expression_wrapper():
    example = ExampleFactory.create()
    assert example.expression_wrapper == "foofoo"


def test_lookup_property__upper():
    example = ExampleFactory.create()
    assert example.upper == "FOO"


def test_lookup_property__lower():
    example = ExampleFactory.create()
    assert example.lower == "foo"


def test_lookup_property__lpad():
    example = ExampleFactory.create()
    assert example.lpad == ".................foo"


def test_lookup_property__rpad():
    example = ExampleFactory.create()
    assert example.rpad == "foo................."


def test_lookup_property__rtrim():
    example = ExampleFactory.create(first_name="foo  ")
    assert example.rtrim == "foo"


def test_lookup_property__ltrim():
    example = ExampleFactory.create(first_name="   foo")
    assert example.ltrim == "foo"


def test_lookup_property__length():
    example = ExampleFactory.create()
    assert example.length == 3


def test_lookup_property__concat():
    example = ExampleFactory.create()
    assert example.concat == "foo bar"


def test_lookup_property__left():
    example = ExampleFactory.create()
    assert example.left == "f"


def test_lookup_property__right():
    example = ExampleFactory.create()
    assert example.right == "o"


def test_lookup_property__repeat():
    example = ExampleFactory.create()
    assert example.repeat == "foofoofoo"


def test_lookup_property__replace():
    example = ExampleFactory.create()
    assert example.replace == "fuu"


def test_lookup_property__reverse():
    example = ExampleFactory.create()
    assert example.reverse == "oof"


def test_lookup_property__strindex():
    example = ExampleFactory.create()
    assert example.strindex == 2


def test_lookup_property__substr():
    example = ExampleFactory.create()
    assert example.substr == "oo"


def test_lookup_property__substr_length():
    example = ExampleFactory.create()
    assert example.substr_length == "o"


def test_lookup_property__trim_length():
    example = ExampleFactory.create(first_name="  foo  ")
    assert example.trim == "foo"


def test_lookup_property__chr():
    example = ExampleFactory.create()
    assert example.chr_ == "A"


def test_lookup_property__ord():
    example = ExampleFactory.create()
    assert example.ord_ == 102


def test_lookup_property__md5():
    example = ExampleFactory.create()
    assert example.md5 == "acbd18db4cc2f85cedef654fccc4a4d8"


def test_lookup_property__sha1():
    example = ExampleFactory.create()
    assert example.sha1 == "0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33"


def test_lookup_property__sha224():
    example = ExampleFactory.create()
    assert example.sha224 == "0808f64e60d58979fcb676c96ec938270dea42445aeefcd3a4e6f8db"


def test_lookup_property__sha256():
    example = ExampleFactory.create()
    assert example.sha256 == "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"


def test_lookup_property__sha384():
    example = ExampleFactory.create()
    assert (
        example.sha384
        == "98c11ffdfdd540676b1a137cb1a22b2a70350c9a44171d6b1180c6be5cbb2ee3f79d532c8a1dd9ef2e8e08e752a3babb"
    )


def test_lookup_property__sha512():
    example = ExampleFactory.create()
    assert example.sha512 == (
        "f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc663832"
        "6e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7"
    )


def test_lookup_property__case():
    example = ExampleFactory.create()
    assert example.case == "foo"


def test_lookup_property__case_2():
    example = ExampleFactory.create()
    assert example.case_2 == "bar"


def test_lookup_property__case_3():
    example = ExampleFactory.create()
    assert example.case_3 == "fizz"


def test_lookup_property__case_4():
    example = ExampleFactory.create()
    assert example.case_4 == "foo"


def test_lookup_property__case_5():
    total = TotalFactory.create(number=1)
    assert total.example.case_5 == "foo"


def test_lookup_property__case_6():
    example = ExampleFactory.create(parts__far__number=1)
    assert example.case_6 == "foo"


def test_lookup_property__case_7():
    example = ExampleFactory.create(parts__number=1, parts__far__number=1)
    assert example.case_7 == "foo"


def test_lookup_property__cast():
    example = ExampleFactory.create()
    assert example.cast_float == 18.0
    assert isinstance(example.cast_float, float)


def test_lookup_property__coalesce():
    example = ExampleFactory.create()
    assert example.coalesce == "foo"


def test_lookup_property__coalesce__second():
    example = ExampleFactory.create(first_name=None)
    assert example.coalesce == "bar"


def test_lookup_property__coalesce__none():
    example = ExampleFactory.create(first_name=None, last_name=None)
    assert example.coalesce is None


def test_lookup_property__coalesce_2():
    example = ExampleFactory.create()
    assert example.coalesce_2 == "foobar"


def test_lookup_property__greatest():
    example = ExampleFactory.create()
    assert example.greatest == 18


def test_lookup_property__greatest__second():
    example = ExampleFactory.create(age=None)
    assert example.greatest == 12


def test_lookup_property__greatest__none():
    example = ExampleFactory.create(age=None, number=None)
    assert example.greatest is None


def test_lookup_property__least():
    example = ExampleFactory.create()
    assert example.least == 12


def test_lookup_property__least__second():
    example = ExampleFactory.create(number=None)
    assert example.least == 18


def test_lookup_property__least__none():
    example = ExampleFactory.create(age=None, number=None)
    assert example.least is None


def test_lookup_property__json_object():
    example = ExampleFactory.create()
    assert example.json_object == {"name": "FOO BAR", "alias": "alias", "age": 36}


def test_lookup_property__nullif():
    example = ExampleFactory.create()
    assert example.nullif == "foo"


def test_lookup_property__nullif__equal():
    example = ExampleFactory.create(last_name="foo")
    assert example.nullif is None


def test_lookup_property__subquery():
    example = ExampleFactory.create()
    ThingFactory.create(example=example, number=12)
    assert example.subquery == 12
