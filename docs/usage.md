# Usage

## Filtering

You can use the lookup property in queries by referring to it inside a special `L` expression:

```pycon
>>> from myapp.models import Student
>>> from lookup_property import L
>>>
>>> Student.objects.create(first_name="John", last_name="Doe")
>>> Student = Student.objects.filter(L(full_name="John Doe")).first()
```

The `L` expression will find the lookup property on the model, and replace it with the
expression defined by it. This allows you to use the property in queries as
if it was a normal field.

You can also use the lookup property as the filter value:

```pycon
>>> Person.objects.filter(first_name=L("full_name"))
```

For more complex filters, `L` expressions can also be used inside `Q` expressions:

```pycon
>>> from django.db.models import Q
>>> Person.objects.filter(Q(first_name=L("full_name")) | Q(L(full_name="John Doe")))
```

## Annotating

You can also annotate the lookup property to pre-calculate it in the QuerySet.

```pycon
>>> Student = Student.objects.annotate(full_name=L("full_name")).first()
>>> Student.full_name
'John Doe'
```

This bypasses the python code/override, which can be more efficient when fetching
multiple rows at once (especially if the property contains complex expressions or joins).

> See the `concrete` argument on `lookup_property` decorator if you always want this behavior.

## Related lookups

The `L` expression also allows you to use the lookup property in related lookups:

```pycon
>>> Class.objects.filter(L(students__full_name="John Doe"))
```

This will find the appropriate model where the lookup property is defined and
add the necessary joins to the query automatically.

## Subqueries

If the lookup property is used in a subquery in an OuterRef, note that the
`L` expression should wrap the whole subquery, and not just the OuterRef, since the
lookup property is located in the outer query model and not the subquery model.

```pycon
>>> from django.db.models import OuterRef, Subquery
>>> from myapp.models import Class, Person
>>>
>>> sq = Class.objecs.filter(teacher_name=OuterRef("full_name")).values("pk")
>>> Person.objects.filter(id__in=L(models.Subquery(sq)))
```

## Additional lookups

Lookup property can be used with additional lookups, such as `__in`, `__lt`, `__gt`, etc.

```pycon
>>> Student.objects.filter(L(full_name__in=["John Doe", "Jane Doe"]))
```

