import datetime

import factory
from factory.django import DjangoModelFactory

from lookup_property.typing import Any, Iterable
from tests.example.models import (
    Alien,
    AnotherConcrete,
    Child,
    Concrete,
    Example,
    Far,
    Other,
    Part,
    Question,
    Thing,
    Total,
)

__all__ = [
    "ChildFactory",
    "ConcreteFactory",
    "ExampleFactory",
    "FarFactory",
    "PartFactory",
    "QuestionFactory",
    "ThingFactory",
    "TotalFactory",
    "AlienFactory",
]


TIMESTAMP = datetime.datetime(2022, 2, 1, tzinfo=datetime.UTC)


class OtherFactory(DjangoModelFactory):
    class Meta:
        model = Other

    @classmethod
    def create(cls, **kwargs: Any) -> Other:
        return super().create(**kwargs)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    @classmethod
    def create(cls, **kwargs: Any) -> Question:
        return super().create(**kwargs)


class ChildFactory(DjangoModelFactory):
    class Meta:
        model = Child

    @classmethod
    def create(cls, **kwargs: Any) -> Child:
        return super().create(**kwargs)


class ExampleFactory(DjangoModelFactory):
    first_name = "foo"
    last_name = "bar"
    age = 18
    number = 12
    timestamp = TIMESTAMP
    other = factory.SubFactory(OtherFactory)
    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Example

    @classmethod
    def create(cls, **kwargs: Any) -> Example:
        return super().create(**kwargs)

    @factory.post_generation
    def children(self, create: bool, items: Iterable[Child] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.children.add(ChildFactory.create(**kwargs))

        for item in items or []:
            self.children.add(item)

    @factory.post_generation
    def parts(self, create: bool, items: Iterable[Part] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            kwargs.setdefault("far__total__example", self)
            self.parts.add(PartFactory.create(**kwargs))

        for item in items or []:
            self.parts.add(item)


class FarFactory(DjangoModelFactory):
    name = "foo"
    number = 12
    total = factory.SubFactory("tests.factories.TotalFactory")

    class Meta:
        model = Far

    @classmethod
    def create(cls, **kwargs: Any) -> Far:
        return super().create(**kwargs)

    @factory.post_generation
    def parts(self, create: bool, items: Iterable[Part] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.parts.add(PartFactory.create(**kwargs))

        for item in items or []:
            self.parts.add(item)


class AlienFactory(DjangoModelFactory):
    name = "foo"
    number = 12
    total = factory.SubFactory("tests.factories.TotalFactory")

    class Meta:
        model = Alien

    @classmethod
    def create(cls, **kwargs: Any) -> Alien:
        return super().create(**kwargs)

    @factory.post_generation
    def parts(self, create: bool, items: Iterable[Part] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.parts.add(PartFactory.create(**kwargs))

        for item in items or []:
            self.parts.add(item)

    @factory.post_generation
    def things(self, create: bool, items: Iterable[Part] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.things.add(ThingFactory.create(**kwargs))

        for item in items or []:
            self.things.add(item)


class ThingFactory(DjangoModelFactory):
    name = "foo"
    number = 12
    example = factory.SubFactory(ExampleFactory)
    far = factory.SubFactory(FarFactory)

    class Meta:
        model = Thing

    @classmethod
    def create(cls, **kwargs: Any) -> Thing:
        return super().create(**kwargs)

    @factory.post_generation
    def aliens(self, create: bool, items: Iterable[Alien] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.aliens.add(AlienFactory.create(**kwargs))

        for item in items or []:
            self.aliens.add(item)


class TotalFactory(DjangoModelFactory):
    name = "foo"
    number = 12
    example = factory.SubFactory(ExampleFactory)

    class Meta:
        model = Total

    @classmethod
    def create(cls, **kwargs: Any) -> Total:
        return super().create(**kwargs)


class PartFactory(DjangoModelFactory):
    name = "foo"
    number = 12
    far = factory.SubFactory(FarFactory)

    class Meta:
        model = Part

    @classmethod
    def create(cls, **kwargs: Any) -> Part:
        return super().create(**kwargs)

    @factory.post_generation
    def examples(self, create: bool, items: Iterable[Example] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.examples.add(ExampleFactory.create(**kwargs))

        for item in items or []:
            self.examples.add(item)

    @factory.post_generation
    def aliens(self, create: bool, items: Iterable[Alien] | None, **kwargs: Any) -> None:
        if not create:
            return

        if items is None and kwargs:
            self.aliens.add(AlienFactory.create(**kwargs))

        for item in items or []:
            self.aliens.add(item)


class ConcreteFactory(DjangoModelFactory):
    abstract_field = "abstract property"
    concrete_field = "concrete property"

    class Meta:
        model = Concrete

    @classmethod
    def create(cls, **kwargs: Any) -> Concrete:
        return super().create(**kwargs)


class AnotherConcreteFactory(DjangoModelFactory):
    abstract_field = "abstract property"
    another_abstract_field = "another abstract property"
    another_concrete_field = "another concrete property"

    class Meta:
        model = AnotherConcrete

    @classmethod
    def create(cls, **kwargs: Any) -> AnotherConcrete:
        return super().create(**kwargs)
