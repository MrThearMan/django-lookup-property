import re

import pytest
from django.db import models
from django.db.models.functions import Extract, Trunc

from lookup_property import expression_to_ast
from lookup_property.converters import convert_django_field
from lookup_property.typing import State


def test_convert_django_field__unknown():
    class MyField(models.Field):
        pass

    msg = re.escape("No implementation for field 'MyField'.")
    with pytest.raises(ValueError, match=msg):
        convert_django_field(MyField(), state=State())


def test_expression_to_ast__trunc__unknown():
    msg = re.escape("No implementation for trunc expression 'foo'.")
    with pytest.raises(ValueError, match=msg):
        expression_to_ast(Trunc("unknown", "foo"), state=State())


def test_expression_to_ast__extract__unknown():
    msg = re.escape("No implementation for extract expression 'foo'.")
    with pytest.raises(ValueError, match=msg):
        expression_to_ast(Extract("unknown", "foo"), state=State())
