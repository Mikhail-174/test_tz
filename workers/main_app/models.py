from django.db import models
from django.contrib.auth.models import User
import uuid

class Worker(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True) #db_index=True
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    hired_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Position(models.Model):
    name = models.CharField(max_length=100)


