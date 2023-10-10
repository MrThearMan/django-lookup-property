import datetime

import pytest
from freezegun import freeze_time

from tests.factories import ExampleFactory

pytestmark = [
    pytest.mark.django_db,
]


@freeze_time("2000-01-01T00:00:00")
def test_lookup_property__now():
    example = ExampleFactory.create()
    assert example.now == datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)


def test_lookup_property__trunc():
    example = ExampleFactory.create()
    assert example.trunc == 2022


def test_lookup_property__trunc_year():
    example = ExampleFactory.create()
    assert example.trunc_year == 2022


def test_lookup_property__trunc_month():
    example = ExampleFactory.create()
    assert example.trunc_month == 2


def test_lookup_property__trunc_day():
    example = ExampleFactory.create()
    assert example.trunc_day == 1


def test_lookup_property__trunc_hour():
    example = ExampleFactory.create()
    assert example.trunc_hour == 0


def test_lookup_property__trunc_minute():
    example = ExampleFactory.create()
    assert example.trunc_minute == 0


def test_lookup_property__trunc_second():
    example = ExampleFactory.create()
    assert example.trunc_second == 0


def test_lookup_property__trunc_week():
    example = ExampleFactory.create()
    assert example.trunc_week == datetime.datetime(2022, 1, 31, tzinfo=datetime.UTC)


def test_lookup_property__trunc_quarter():
    example = ExampleFactory.create()

    assert example.trunc_quarter == datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC)


def test_lookup_property__trunc_date():
    example = ExampleFactory.create()

    assert example.trunc_date == datetime.date(2022, 2, 1)


def test_lookup_property__trunc_time():
    example = ExampleFactory.create()

    assert example.trunc_time == datetime.time(tzinfo=datetime.UTC)


def test_lookup_property__extract():
    example = ExampleFactory.create()
    assert example.extract == 2022


def test_lookup_property__extract_year():
    example = ExampleFactory.create()
    assert example.extract_year == 2022


def test_lookup_property__extract_iso_year():
    example = ExampleFactory.create()
    assert example.extract_iso_year == 2022


def test_lookup_property__extract_month():
    example = ExampleFactory.create()
    assert example.extract_month == 2


def test_lookup_property__extract_day():
    example = ExampleFactory.create()
    assert example.extract_day == 1


def test_lookup_property__extract_week():
    example = ExampleFactory.create()
    assert example.extract_week == 5


def test_lookup_property__extract_weekday():
    example = ExampleFactory.create()
    assert example.extract_weekday == 1


def test_lookup_property__extract_iso_weekday():
    example = ExampleFactory.create()
    assert example.extract_iso_weekday == 2


def test_lookup_property__extract_quarter():
    example = ExampleFactory.create()
    assert example.extract_quarter == datetime.datetime(2022, 1, 1, tzinfo=datetime.UTC)


def test_lookup_property__extract_hour():
    example = ExampleFactory.create()
    assert example.extract_hour == 0


def test_lookup_property__extract_minute():
    example = ExampleFactory.create()
    assert example.extract_minute == 0


def test_lookup_property__extract_second():
    example = ExampleFactory.create()
    assert example.extract_second == 0
