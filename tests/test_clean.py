
import pytest
from django.utils import timezone

from tests.example.models import Example
from tests.factories import OtherFactory, QuestionFactory


@pytest.mark.django_db
def test_clean_model_with_lookup_property__kwargs():
    other = OtherFactory.create()
    question = QuestionFactory.create()

    example = Example(
        first_name="first",
        last_name="last",
        number=100,
        age=18,
        timestamp=timezone.now(),
        other=other,
        question=question,
    )

    example.full_clean()
    example.save()


@pytest.mark.django_db
def test_clean_model_with_lookup_property__attrs():
    other = OtherFactory.create()
    question = QuestionFactory.create()

    example = Example()
    example.first_name = "first"
    example.last_name = "last"
    example.number = 100
    example.age = 18
    example.timestamp = timezone.now()
    example.other = other
    example.question = question

    # Somehow, this can fail if `generated=False`
    example.full_clean()
    example.save()
