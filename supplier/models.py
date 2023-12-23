from django.db import models
from django.contrib.auth.models import User


class Supplier(models.Model):
    account = models.OneToOneField(User, on_delete=models.PROTECT, related_name="supplier")
    market = models.CharField(default="sadovod", max_length=255, choices=(("sadovod", "Садовод"), ("yuzhnye_vorota", "Южные ворота")))
    boutique = models.CharField(default="", max_length=255)
    bad_remarks_count = models.PositiveIntegerField(default=0, null=True, blank=True, editable=False)
    good_remarks_count = models.PositiveIntegerField(default=0, null=True, blank=True, editable=False)
