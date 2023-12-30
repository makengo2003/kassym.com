from django import template

from message.models import Message
from project import settings


register = template.Library()


@register.simple_tag
def get_messages_count():
    request_user = getattr(settings, 'request_user', None)
    if request_user.is_authenticated:
        return Message.objects.filter(has_read=False, to_user=request_user).count()
    return 0
