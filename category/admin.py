from django.contrib import admin
from .models import Category, CategoryFiltration, CategoryFiltrationValue

admin.site.register(Category)
admin.site.register(CategoryFiltration)
admin.site.register(CategoryFiltrationValue)
