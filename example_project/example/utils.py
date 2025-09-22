from typing import Any

from django.db import models

__all__ = [
    "SubqueryAggregate",
    "SubqueryCount",
    "SubquerySum",
]


class SubqueryAggregate(models.Subquery):
    template: str = "(SELECT {function}(%(aggregate_field)s) FROM (%(subquery)s) %(alias)s)"
    output_field: models.Field = models.BigIntegerField()
    aggregate: str | None = None
    aggregate_field: str | None = None
    default_alias: str = "_agg"

    def __init__(
        self,
        queryset: models.QuerySet,
        *,
        field: str | None = None,
        alias: str | None = None,
        output_field: models.Field | None = None,
        **kwargs: Any,
    ) -> None:
        self.template = self.template.format(function=self.aggregate)
        kwargs["aggregate_field"] = field or self.aggregate_field
        kwargs["alias"] = alias or self.default_alias
        super().__init__(queryset, output_field, **kwargs)


class SubqueryCount(SubqueryAggregate):
    """
    Count how many rows are returned from a subquery.
    Should be used instead of "Count" when there might be collisions
    between counted related objects and filter conditions.

    >>> class Foo(models.Model):
    >>>     number = models.IntegerField()
    >>>
    >>> class Bar(models.Model):
    >>>     number = models.IntegerField()
    >>>     example = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="bars")
    >>>
    >>> foo = Foo.objects.create(number=1)
    >>> Bar.objects.create(example=foo, number=2)
    >>> Bar.objects.create(example=foo, number=2)
    >>>
    >>> foo = (
    >>>     Foo.objects.annotate(count=models.Count("bars"))
    >>>     .filter(bars__number=2)
    >>>     .first()
    >>> )
    >>> assert foo.count == 2

    This fails and asserts that count is 4. The reason is that Bar objects are
    joined twice: once for the count, and once for the filter. Django does not
    reuse the join, since it is not aware that the join is the same.

    Therefore, do this instead:

    >>> foo = (
    >>>     Foo.objects.annotate(
    >>>         count=SubqueryCount(
    >>>             Bar.objects.filter(example=models.OuterRef("id")).values("id")
    >>>         )
    >>>     )
    >>>     .filter(bars__number=2)
    >>>     .first()
    >>> )
    """

    aggregate = "COUNT"
    aggregate_field = "*"
    default_alias = "_count"


class SubquerySum(SubqueryAggregate):
    aggregate = "SUM"
    default_alias = "_sum"
