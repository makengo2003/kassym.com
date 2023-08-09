from django import template
from site_settings.models import Contact


register = template.Library()


@register.simple_tag
def get_contacts():
    return Contact.objects.all()
