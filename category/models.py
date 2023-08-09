from django.db import models


class Category(models.Model):
    index = models.IntegerField(null=True)
    name = models.CharField(max_length=255)
    is_available = models.BooleanField(default=False)
    poster = models.ImageField(upload_to="category_posters/", max_length=500)


class CategoryFiltration(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="filtration")
    name = models.CharField(max_length=100)


class CategoryFiltrationValue(models.Model):
    category_filtration = models.ForeignKey(CategoryFiltration, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=100)
