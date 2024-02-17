# Converters

> The examples discussed here are already implemented
> and are given just as a simple illustration of usage.

## Expressions

The `@lookup_property` decorator uses a [single-dispatch] function
`lookup_property.converters.expressions.expression_to_ast` to register
a number of converters for transforming Django ORM expressions to
equivalent python statement [AST].

Let's take a look at our example from before:

```python
from lookup_property import lookup_property
from django.db import models
from django.db.models import Value
from django.db.models.functions import Concat

class Student(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    @lookup_property
    def full_name(self):
        return Concat("first_name", Value(" "), "last_name")
```

Here are the converters required to transform this to a python statement AST:

```python
import ast
from django.db import models
from django.db.models import functions
from lookup_property import expression_to_ast, State
from lookup_property.converters.utils import ast_property

@expression_to_ast.register
def _(expression: str, state: State) -> ast.Constant:
    # Called by converters for Value and ConcatPair to convert
    # the strings they contain to ast constants.
    return ast.Constant(value=expression)

@expression_to_ast.register
def _(expression: models.Value, state: State) -> ast.AST:
    # Convert the `value` inside the Value-class to ast constant.
    # Notice `expression_to_ast` is called recursively.
    return expression_to_ast(expression.value, state)

@expression_to_ast.register
def _(expression: models.F, state: State) -> ast.Attribute:
    # Convert F-objects to self-attributes.
    # This is such a common operation that the library provides a utility for it.
    return ast_property(expression.name)

@expression_to_ast.register
def _(expression: functions.Concat, state: State) -> ast.AST:
    # Concat is composed of nested ConcatPair-expressions:
    # Concat((ConcatPair("foo", ConcatPair("bar", "baz"))))
    # Convert the concat pairs recursively.
    source_expressions = expression.get_source_expressions()
    return expression_to_ast(source_expressions[0], state)

@expression_to_ast.register
def _(expression: functions.ConcatPair, state: State) -> ast.BinOp:
    # First convert the left and right ConcatPair elements
    # to their AST nodes (string constants in this case)
    # and then compose them into a BinOp (left + right)
    source_expressions = expression.get_source_expressions()
    left = expression_to_ast(source_expressions[0], state)
    right = expression_to_ast(source_expressions[1], state)
    return ast.BinOp(left=left, op=ast.Add(), right=right)
```

## Lookups

To convert [lookups] inside `L` and `Q` expressions, there is another single-dispatch
function `lookup_property.converters.lookups.lookup_to_ast`.

For example, to convert the following lookup-property:

```python
from lookup_property import lookup_property
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=256)

    @lookup_property
    def start_with_letter_a(self):
        return models.Q(name__startswith="A")
```

Here's the lookup converter required to transform this to a python statement AST:

```python
import ast
from django.db.models import lookups
from lookup_property import lookup_to_ast, expression_to_ast, State
from lookup_property.converters.utils import ast_method

# This is a custom single-dispatch function, and registering works
# a bit differently: `lookup` keyword must be specified for register.
# Q(foo__bar__lookup=val) -> (attrs: ["foo", "bar"], value: val)
@lookup_to_ast.register(lookup=lookups.StartsWith.lookup_name)
def _(attrs: list[str], value: str, state: State) -> ast.Call:
    # `ast_method` is another utility function, which outputs the AST
    # for a method like: self.foo.bar.method(*args, **kwargs)
    return ast_method("startswith", attrs, expression_to_ast(value, state))
```

## Casts

Yet another single-dispatch function exists for the Cast operation,
and can be used to select a proper callable for conversion.

```python
import ast
from django.db import models
from lookup_property import State, convert_django_field

@convert_django_field.register
def _(field: models.BooleanField, state: State) -> ast.Name:
    # Should return the name of the function that can be used
    # to convert to the given model field type
    return ast.Name(id="bool", ctx=ast.Load())
```

[single-dispatch]: https://peps.python.org/pep-0443/
[AST]: https://docs.python.org/3/library/ast.html
[lookups]: https://docs.djangoproject.com/en/4.2/ref/models/lookups/
