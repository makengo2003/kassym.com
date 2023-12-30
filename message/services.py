from django.db.models import Q
from django_bulk_update.helper import bulk_update

from message.models import Message
from product.models import Product
from user.models import MyCard


def get_messages_preview_data(user):
    product_status_last_message = Message.objects.filter(to_user=user, type="product_status").last()
    if product_status_last_message:
        product_status_last_message = product_status_last_message.text
    else:
        product_status_last_message = ""

    order_status_last_message = Message.objects.filter(to_user=user, type="order_status").last()
    if order_status_last_message:
        order_status_last_message = order_status_last_message.text
    else:
        order_status_last_message = ""

    news_last_message = Message.objects.filter(to_user=user, type="news").last()
    if news_last_message:
        news_last_message = news_last_message.text
    else:
        news_last_message = ""

    tech_support_last_message = Message.objects.filter(to_user=user, type="tech_support").last()
    if tech_support_last_message:
        tech_support_last_message = tech_support_last_message.text
    else:
        tech_support_last_message = ""

    messages = {
        "product_status": {
            "last_message": product_status_last_message,
            "has_not_read_count": Message.objects.filter(to_user=user, has_read=False, type="product_status").count()
        },
        "order_status": {
            "last_message": order_status_last_message,
            "has_not_read_count": Message.objects.filter(to_user=user, has_read=False, type="order_status").count()
        },
        "news": {
            "last_message": news_last_message,
            "has_not_read_count": Message.objects.filter(to_user=user, has_read=False, type="news").count()
        },
        "tech_support": {
            "last_message": tech_support_last_message,
            "has_not_read_count": Message.objects.filter(to_user=user, has_read=False, type="tech_support").count()
        },
    }

    return messages


def get_messages(user, message_type):
    messages = Message.objects.filter(to_user=user, type=message_type).order_by("-id")[:500:-1]
    Message.objects.filter(to_user=user, type=message_type, has_read=False).update(has_read=True)
    return messages


def create_product_status_messages(product_id):
    product = Product.objects.filter(id=product_id).only("is_available", "count").first()

    if product.is_available:
        if 20 >= product.count > 0:
            status = "less_than_20"
            text = f'Количество товара "{product.name}" составляет менее 20 единиц. Пожалуйста, следите за наличием товаров!'
        else:
            status = "available"
            text = f'Товар "{product.name}" в наличии.'
    else:
        status = "not_available"
        text = f'К сожалению, товар "{product.name}" сейчас недоступен. Мы работаем над пополнением запасов. Следите за нашими обновлениями.'

    messages = []
    my_cards = MyCard.objects.filter(~Q(last_status=status), product_id=product_id).only("user_id", "last_status")

    for my_card in my_cards:
        messages.append(Message(type="product_status", to_user_id=my_card.user_id, text=text))
        my_card.last_status = status

    bulk_update(my_cards, update_fields=["last_status"])
    Message.objects.bulk_create(messages)
