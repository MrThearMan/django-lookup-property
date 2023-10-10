import uuid

from django.db import models

from lookup_property import lookup_property


class Person(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()

    @lookup_property
    def reverse_one_to_one(self):
        return models.F("address__pk")

    @reverse_one_to_one.override
    def _(self):
        return self.address.pk


class Address(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    person = models.OneToOneField(
        Person,
        related_name="address",
        on_delete=models.CASCADE,
    )
