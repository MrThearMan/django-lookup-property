from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Iterator

from django.db import models
from django.db.models import ForeignObjectRel
from django.db.models.constants import LOOKUP_SEP

from lookup_property.expressions import LookupPropertyCol

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
        self.model = model
        self.target_property = target_property
        if target_property.state.joins:
            self.path_infos = LazyPathInfo(self)

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
        private_only: bool = False,  # noqa: FBT001, FBT002, ARG002
    ) -> None:
        # Register property on a concrete implementation of an abstract model
        if cls != self.model:
            field = LookupPropertyField(cls, target_property=self.target_property)
            field.set_attributes_from_name(name)
            cls._meta.add_field(field, private=True)


class LazyPathInfo:
    """
    Class used to `trick django.db.models.sql.query.Query.names_to_path`
    into thinking that a LookupPropertyField is a related field, like a
    ForeignKey or OneToOneField. Computes a list of PathInfo objects, which
    will the be used by `django.db.models.sql.query.JoinPromoter` to add
    sql joins to the query, e.g., for `queryset.count()`.
    """

    def __init__(self, field: LookupPropertyField) -> None:
        self.field = field

    def __iter__(self) -> Iterator[PathInfo]:
        return iter([self[0]])

    def __getitem__(self, item: int) -> PathInfo:
        return self.get_path_info[item]

    @cached_property
    def get_path_info(self) -> list[PathInfo]:
        parts: list[str] = self.field.expression.name.split(LOOKUP_SEP)
        rel_or_field: ForeignObjectRel | ForeignObject | ManyToManyField = self.field.model._meta.get_field(parts[0])

        # Forward relation
        if isinstance(rel_or_field, ForeignObjectRel):
            return rel_or_field.field.get_reverse_path_info()
        # Reverse relation
        return rel_or_field.get_path_info()
