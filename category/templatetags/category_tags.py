from django import template
from category import services as category_services
from category.models import Category
from project.settings import MAIN_CATEGORY_ID
from django.db.models import Count


register = template.Library()


@register.simple_tag
def get_categories():
    return category_services.get_categories(serialize=False)


@register.simple_tag
def get_main_category():
    return Category.objects.filter(id=MAIN_CATEGORY_ID).annotate(products_count=Count("products__id")).first()
