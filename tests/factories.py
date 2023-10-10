import datetime

import factory
from factory.django import DjangoModelFactory

from lookup_property.typing import Any, Iterable
from tests.example.models import Example, Other, Part, Thing, Total

__all__ = [
    "ExampleFactory",
    "PartFactory",
    "ThingFactory",
    "TotalFactory",
]


TIMESTAMP = datetime.datetime(2022, 2, 1, tzinfo=datetime.UTC)


class OtherFactory(DjangoModelFactory):
    class Meta:
        model = Other

    @classmethod
    def create(cls, **kwargs: Any) -> Other:
        return super().create(**kwargs)


class ExampleFactory(DjangoModelFactory):
    first_name = "foo"
    last_name = "bar"
    age = 18
    number = 12
    timestamp = TIMESTAMP
    other = factory.SubFactory(OtherFactory)

    class Meta:
        model = Example

    @classmethod
    def create(cls, **kwargs: Any) -> Example:
        return super().create(**kwargs)


class ThingFactory(DjangoModelFactory):
    name = "foo"
    example = factory.SubFactory(ExampleFactory)

    class Meta:
        model = Thing

    @classmethod
    def create(cls, **kwargs: Any) -> Thing:
        return super().create(**kwargs)


class TotalFactory(DjangoModelFactory):
    name = "foo"
    example = factory.SubFactory(ExampleFactory)

    class Meta:
        model = Total

    @classmethod
    def create(cls, **kwargs: Any) -> Total:
        return super().create(**kwargs)


class PartFactory(DjangoModelFactory):
    name = "foo"

    class Meta:
        model = Part

    @factory.post_generation
    def examples(self, create: bool, items: Iterable[Example] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.examples.add(ExampleFactory.create())

        for item in items or []:
            self.examples.add(item)

    @classmethod
    def create(cls, **kwargs: Any) -> Part:
        return super().create(**kwargs)
