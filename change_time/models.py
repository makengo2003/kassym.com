from django.db import models


class ChangeTime(models.Model):
    dt = models.DateField(unique=True)
