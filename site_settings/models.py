from django.db import models


CONTACT_TYPES = (
    ("phone_number", "Номер телефона"),
    ("whatsapp", "Whatsapp"),
    ("email", "Эл. почта"),
    ("instagram", "Instagram"),
    ("order_manager", "Номер менеджера по заказам"),
    ("footer", "Footer"),
    ("telegram_chat_id", "Ваш Chat Id в Telegram")
)


class Contact(models.Model):
    contact = models.CharField(max_length=500)
    link = models.CharField(max_length=500, default="")
    type = models.CharField(max_length=100, choices=CONTACT_TYPES, unique=True)


class Slide(models.Model):
    image = models.ImageField(upload_to="slide_images/")
    link = models.CharField(max_length=500, default="/")
