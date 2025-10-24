from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.postgres.indexes import HashIndex

class Worker(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    hired_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)

class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
# from faker import Faker
# import random
#
# the_fake = Faker()
# for i in range(10000):
#     positions = Position.objects.all()
#
#     new = Worker(first_name=the_fake.first_name(), last_name=the_fake.last_name(), email=f"{the_fake.name()}{i}@gmail.com", position=random.choice(positions))
#     new.save()