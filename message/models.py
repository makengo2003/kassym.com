from django.db import models
from django.contrib.auth.models import User

from project.utils import datetime_now


class Message(models.Model):
    type = models.CharField(max_length=255, choices=(("product_status", "Остатки"), ("order_status", "Мои заказы"),
                                                     ("news", "Новости"), ("tech_support", "Тех. поддержка")))
    text = models.TextField()
    dt = models.DateTimeField(default=datetime_now, editable=False)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_from_me", null=True, blank=True)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_to_me")
    has_read = models.BooleanField(default=False, editable=False)

    def get_formatted_dt(self):
        return self.dt.strftime("%d.%m.%Y, %H:%M")


class MessageFile(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="message_files/")
