from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone

import uuid
import datetime

from .managers import IsDeletedManager


class Worker(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    hired_date = models.DateTimeField(auto_now_add=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    objects = IsDeletedManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.email}"

    @admin.display(
        boolean=True,
        ordering="position",
        description="Developers",
    )
    def is_a_developer(self):
        return 'developer' in self.position.name.lower()

    @admin.display(
        boolean=True,
        ordering="hired_date",
        description="Recently hired?",
    )
    def was_hired_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.hired_date <= now

    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"
        ordering = ['hired_date']

class Position(models.Model):
    name = models.CharField(max_length=100)
    # name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


# from faker import Faker
# import random
#
# the_fake = Faker()
# for i in range(10000):
#     positions = Position.objects.all()
#
#     new = Worker(first_name=the_fake.first_name(), last_name=the_fake.last_name(), email=f"{the_fake.name()}{i}@gmail.com", position=random.choice(positions))
#     new.save()