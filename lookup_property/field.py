from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Iterator

from django.db import models
from django.db.models import ForeignObjectRel
from django.db.models.constants import LOOKUP_SEP

from lookup_property.expressions import LookupPropertyCol
from lookup_property.typing import Sentinel

if TYPE_CHECKING:
    from django.db.models.fields.related import ForeignObject, ManyToManyField
    from django.db.models.query_utils import PathInfo

    from lookup_property.decorator import lookup_property
    from lookup_property.typing import Expr

__all__ = [
    "LookupPropertyField",
]


class LookupPropertyField(models.Field):
    def __init__(self, model: type[models.Model], target_property: lookup_property) -> None:
        self.model = model  # Required by `LookupPropertyCol` to resolve related lookups
        self.target_property = target_property
        if target_property.state.joins:
            self.path_infos = LazyPathInfo(self, joins=target_property.state.joins)

        super().__init__()
        target_property.field = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    @property
    def expression(self) -> Expr:
        return self.target_property.expression

    def get_col(  # type: ignore[override]
        self,
        alias: str,  # noqa: ARG002
        output_field: models.Field | None = None,  # noqa: ARG002
    ) -> LookupPropertyCol:
        return self.cached_col

    @cached_property
    def cached_col(self) -> LookupPropertyCol:  # type: ignore[override]
        return LookupPropertyCol(target_field=self)

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        # Register property on a concrete implementation of an abstract model
        self.target_property.contribute_to_class(cls, name, private_only=private_only)

    def get_default(self) -> Any:
        # Default value that makes sure `lookup_property.__get__`
        # does not consider the field as set right after initialization.
        # Called by `Model.__init__`.
        return Sentinel


class LazyPathInfo:
    """
    Class used to `trick django.db.models.sql.query.Query.names_to_path`
    into thinking that a LookupPropertyField is a related field, like a
    ForeignKey or OneToOneField. Computes a list of PathInfo objects, which
    will the be used by `django.db.models.sql.query.JoinPromoter` to add
    sql joins to the query, e.g., for `queryset.count()`.
    """

    def __init__(self, field: LookupPropertyField, *, joins: list[str] | bool = True) -> None:
        self.field = field
        self.joins: list[str] = joins if isinstance(joins, list) else []

    def __iter__(self) -> Iterator[PathInfo]:
        return iter([self[0]])

    def __getitem__(self, item: int) -> PathInfo:
        return self.get_path_info[item]

    @cached_property
    def get_path_info(self) -> list[PathInfo]:
        joins = self.joins
        if not joins:
            expression = self.field.expression
            while hasattr(expression, "source_expressions"):
                expression = expression.source_expressions[0]

            joins = expression.name.split(LOOKUP_SEP)[:1]

        path_info: list[PathInfo] = []
        for join in joins:
            rel_or_field: ForeignObjectRel | ForeignObject | ManyToManyField
            rel_or_field = self.field.model._meta.get_field(join)  # type: ignore[assignment]

            if isinstance(rel_or_field, ForeignObjectRel):
                path_info.extend(rel_or_field.field.get_reverse_path_info())
            else:
                path_info.extend(rel_or_field.get_path_info())

        return path_info
