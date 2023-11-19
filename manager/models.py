from django.db import models
from django.contrib.auth.models import User


class Manager(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name="manager")
