import json

from django import template
from site_settings.models import Contact
from site_settings import services


register = template.Library()


@register.simple_tag
def get_contacts():
    return Contact.objects.all()


@register.simple_tag
def get_slides():
    return services.get_slides()
