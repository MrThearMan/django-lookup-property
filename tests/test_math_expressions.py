import math

import pytest

from tests.factories import ExampleFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_lookup_property__abs():
    example = ExampleFactory.create()
    assert example.abs_ == 12


def test_lookup_property__acos():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.acos, 0.0) is True


def test_lookup_property__asin():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.asin, 1.5707963267948966) is True


def test_lookup_property__atan():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.atan, 0.7853981633974483) is True


def test_lookup_property__atan2():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.atan2, 0.4636476090008061) is True


def test_lookup_property__ceil():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.ceil, 1.0) is True


def test_lookup_property__cos():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.cos, 0.5403023058681398) is True


def test_lookup_property__cot():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.cot, 0.6420926159343306) is True


def test_lookup_property__degrees():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.degrees, 57.29577951308232) is True


def test_lookup_property__exp():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.exp, 2.718281828459045) is True


def test_lookup_property__floor():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.floor, 1.0) is True


def test_lookup_property__ln():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.ln, 0.0) is True


def test_lookup_property__log():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.log, 0.0) is True


def test_lookup_property__mod():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.mod, 1.0) is True


def test_lookup_property__pi():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.pi, 3.141592653589793) is True


def test_lookup_property__power():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.power, 1.0) is True


def test_lookup_property__radians():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.radians, 0.017453292519943295) is True


def test_lookup_property__random():
    example = ExampleFactory.create(number=1)
    assert 0 <= example.random < 1


def test_lookup_property__round():
    example = ExampleFactory.create(number=1.111)
    assert math.isclose(example.round_, 1) is True


def test_lookup_property__round_2():
    example = ExampleFactory.create(number=1.111)
    assert math.isclose(example.round_2, 1.11) is True


def test_lookup_property__sign():
    example = ExampleFactory.create(number=-10)
    assert math.isclose(example.sign, -1) is True


def test_lookup_property__sin():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.sin, 0.8414709848078965) is True


def test_lookup_property__sqrt():
    example = ExampleFactory.create(number=25)
    assert math.isclose(example.sqrt, 5) is True


def test_lookup_property__tan():
    example = ExampleFactory.create(number=1)
    assert math.isclose(example.tan, 1.5574077246549023) is True
