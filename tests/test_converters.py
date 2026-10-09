import ast
import importlib
import re
import sys

import pytest
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db import models
from django.db.models.expressions import CombinedExpression
from django.db.models.functions import Extract, Now, Trunc

from lookup_property import L, expression_to_ast
from lookup_property.converters import aggregates, cast, convert_django_field
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


def test_expression_to_ast__combined_expression__unknown():
    expression = CombinedExpression(models.F("foo"), "@@", models.F("bar"))

    msg = re.escape("No implementation for connector '@@'.")
    with pytest.raises(ValueError, match=msg):
        expression_to_ast(expression, state=State())


def test_expression_to_ast__now__no_timezone():
    node = expression_to_ast(Now(), state=State(use_tz=False))
    assert ast.unparse(node) == "datetime.datetime.now()"


def test_expression_to_ast__l_ref():
    node = expression_to_ast(L("foo__bar"), state=State())
    assert ast.unparse(node) == "self.foo.bar"


def test_expression_to_ast__l_lookup():
    node = expression_to_ast(L(foo__bar="baz"), state=State())
    assert ast.unparse(node) == "self.foo.bar == 'baz'"



def test_expression_to_ast__postgres_aggregate():
    state = State()
    node = expression_to_ast(ArrayAgg("foo"), state=state)

    arg_name = next(iter(state.extra_kwargs))
    assert ast.unparse(node) == f"self.__class__.objects.aggregate({arg_name}={arg_name}())['{arg_name}']"


def test_convert_django_field__array_field():
    node = convert_django_field(ArrayField(models.IntegerField()), state=State())
    assert ast.unparse(node) == "list"


def test_convert_django_field__hstore_field():
    node = convert_django_field(HStoreField(), state=State())
    assert ast.unparse(node) == "dict"


@pytest.mark.parametrize(
    ("module", "import_name"),
    [
        (aggregates, "django.contrib.postgres"),
        (cast, "django.contrib.postgres.fields"),
    ],
)
def test_converters__postgres_not_installed(module, import_name, monkeypatch):
    # Importing a module that is None in 'sys.modules' raises 'ModuleNotFoundError'.
    monkeypatch.setitem(sys.modules, import_name, None)

    importlib.reload(module)
