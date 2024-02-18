# Introduction

## Simple use case

Let's say we have a model with two fields, `first_name` and `last_name`.
We want to create a property `full_name` that concatenates the two fields,
but we also want to use this property in a queryset to filter rows. Furthermore,
we want this to work from related models as well.

Normally, we would need to create the property and the ORM expression separately -
the property on the model and the expression in the queryset, creating duplication and
distance between the two pieces of code. To be able to use the filter from related models,
we would also need to create some function to generate the expression with the necessary
joins for each situation it is used in.

For simple properties, you might just write the expression multiple times,
but for more complex properties this will introduce a lot of complexity that
you need to keep in sync.

Lookup property allows us to define the property and ORM expression in one go,
and then use the property in a queryset, even on related models.

```python
from lookup_property import lookup_property
from django.db import models
from django.db.models import Value
from django.db.models.functions import Concat

class Student(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    @lookup_property
    def full_name():
        return Concat("first_name", Value(" "), "last_name")
```

> Django 5.0 introduced [GeneratedField], which can be used
> for this purpose. However, it's not as flexible as the lookup property,
> and doesn't support all the features of the Django ORM, mainly
> related lookups. We'll go over these in more detail later.

## Overview

The method decorated by the `lookup_property` decorator is added the model
as a special `LookupPropertyField`. This allows QuerySets to find it from the model.

The method should be static, and return a Django ORM expression,
which is used as the value of the field in QuerySets. Even though the method
is static, you can still refer to other fields on the model using Django's `F` object.

For the python property, the expression is converted to a regular python code
using pre-defined converters. The converters create a python [AST] from the expression,
which is then evaluated using `eval()`. The library already provides converters for
most of the common expressions, but it's also possible to register new converters or
replace existing ones (see. [converters](/converters/)).

> While use of `eval()` should generally be avoided due to security
> concerns, here the risks are minimal, since the evaluation only happens
> once during class creation, and from existing code rather than user input.
> Still, any extensions like new converters should keep this in mind,
> and not, for example, read any input from a database during the conversion process.

You can inspect the generated python source from the class:

```pycon
>>> Student.full_name.func_source
"""
def full_name(self):
    return self.first_name + (' ' + self.last_name)
"""
```

> Notice that the generated expression _does_ contain a self-reference, even though
> the original lookup property didn't. This is for `F` expressions to be able to reference
> the fields on the model.

You should always inspect and test the generated source to make sure it's what you expect,
especially if you're using complex expressions or custom converters.

## Override

If you don't like the python auto-generation, or want to write a more optimal code yourself,
you can override the generated expression with a custom one:

```python
from lookup_property import lookup_property
from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    @lookup_property(skip_codegen=True)
    def full_name():
        return ...

    @full_name.override
    def _(self):
        return f"{self.first_name} {self.last_name}"
```

> By doing this, you'll be trading reduced code duplication for correctness and performance,
> and you'll need start keeping the expression in sync with the property manually.

The use of the `skip_codegen` argument is required when using overrides. Otherwise, the
lookup expression would try to convert the expression the python code, only to be overridden.
We need to explicitly tell this to the lookup property, because the conversion happens immediately
at class creation time, and the override is only added to the class after it.

## Related models

Lookup properties can also reference related models. While some expressions _might_
work without any additional setup in some cases, it's recommended to specify the
`joins` in for these lookup properties manually.

```python
from lookup_property import lookup_property
from django.db import models

class Student(models.Model):
    ...

    @lookup_property(joins=["classes"])
    def number_of_classes(self):
        return models.Count("classes")

class Class(models.Model):
    students = models.ManyToManyField(Student, related_name="classes")
    ...
```

## Concrete properties

Lookup properties are not included in select statements by default. This is because
the properties can contain joins, which we might not want to do for every query.

If you do want this behavior, you can use the `concrete` argument to always
"annotate" the lookup property on the model when it is fetched from the database:

```python
from lookup_property import lookup_property
from django.db import models

class Student(models.Model):
    ...

    @lookup_property(concrete=True)
    def full_name():
        return ...
```


[AST]: https://docs.python.org/3/library/ast.html
[descriptor]: https://docs.python.org/3/howto/descriptor.html
[GeneratedField]: https://docs.djangoproject.com/en/5.0/ref/models/fields/#generatedfield
