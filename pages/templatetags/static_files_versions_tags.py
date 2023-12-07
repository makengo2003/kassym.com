from django import template
from project.settings import SERVER_RAN_TIME


register = template.Library()


@register.simple_tag
def get_server_ran_time():
    return SERVER_RAN_TIME
