# Django Lookup Property

[![Coverage Status][coverage-badge]][coverage]
[![GitHub Workflow Status][status-badge]][status]
[![PyPI][pypi-badge]][pypi]
[![GitHub][licence-badge]][licence]
[![GitHub Last Commit][repo-badge]][repo]
[![GitHub Issues][issues-badge]][issues]
[![Downloads][downloads-badge]][pypi]
[![Python Version][version-badge]][pypi]

```shell
pip install django-lookup-property
```

---

**Documentation**: [https://mrthearman.github.io/django-lookup-property/](https://mrthearman.github.io/django-lookup-property/)

**Source Code**: [https://github.com/MrThearMan/django-lookup-property/](https://github.com/MrThearMan/django-lookup-property/)

**Contributing**: [https://github.com/MrThearMan/django-lookup-property/blob/main/CONTRIBUTING.md](https://github.com/MrThearMan/django-lookup-property/blob/main/CONTRIBUTING.md)

---

Django model properties that are also lookup expressions.

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
```pycon
>>> from myapp.models import Student
>>> from lookup_property import L
>>>
>>> Student.objects.create(first_name="John", last_name="Doe")
>>> student = Student.objects.filter(L(full_name="John Doe")).first()
>>>
>>> student.full_name
'John Doe'
```

[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/django-lookup-property/badge.svg?branch=main
[status-badge]: https://img.shields.io/github/actions/workflow/status/MrThearMan/django-lookup-property/test.yml?branch=main
[pypi-badge]: https://img.shields.io/pypi/v/django-lookup-property
[licence-badge]: https://img.shields.io/github/license/MrThearMan/django-lookup-property
[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/django-lookup-property
[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/django-lookup-property
[version-badge]: https://img.shields.io/pypi/pyversions/django-lookup-property
[downloads-badge]: https://img.shields.io/pypi/dm/django-lookup-property

[coverage]: https://coveralls.io/github/MrThearMan/django-lookup-property?branch=main
[status]: https://github.com/MrThearMan/django-lookup-property/actions/workflows/test.yml
[pypi]: https://pypi.org/project/django-lookup-property
[licence]: https://github.com/MrThearMan/django-lookup-property/blob/main/LICENSE
[repo]: https://github.com/MrThearMan/django-lookup-property/commits/main
[issues]: https://github.com/MrThearMan/django-lookup-property/issues
