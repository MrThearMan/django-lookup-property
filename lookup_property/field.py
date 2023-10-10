from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from django.db import models

from lookup_property.expressions import LookupPropertyCol

if TYPE_CHECKING:
    from lookup_property.typing import Expr

__all__ = [
    "LookupPropertyField",
]


class LookupPropertyField(models.Field):
    def __init__(self, model: type[models.Model], expression: Expr) -> None:
        self.model = model
        self.expression = expression
        super().__init__()

    def get_col(  # type: ignore[override]
        self,
        alias: str,  # noqa: ARG002
        output_field: models.Field | None = None,  # noqa: ARG002
    ) -> LookupPropertyCol:
        return self.cached_col

    @cached_property
    def cached_col(self) -> LookupPropertyCol:  # type: ignore[override]
        return LookupPropertyCol(target=self)

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,  # noqa: FBT001, FBT002, ARG002
    ) -> None:  # pragma: no cover
        if cls != self.model:
            field = LookupPropertyField(model=cls, expression=self.expression)
            field.set_attributes_from_name(name)
            cls._meta.add_field(field, private=True)
