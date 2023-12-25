from django.db import models
from django.contrib.auth.models import User


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sum = models.PositiveIntegerField()
    description = models.TextField()
    employee_type = models.CharField(max_length=255, choices=(("buyer", "Закупщик/Сортировщик"), ("manager", "Менеджер")))
    change_time = models.DateField()
    currency = models.CharField(max_length=255, choices=(("ruble", "рубль"), ("tenge", "тенге")), default="ruble")
