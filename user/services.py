from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django_user_agents.utils import get_user_agent

from typing import Mapping, List

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.request import Request

from project.settings import EMAIL_HOST_USER
from site_settings.models import Contact
from .models import FavouriteProduct, Client
from .serializers import ChangePasswordSerializer, ClientSerializer, ClientFormSerializer


def change_password(request: Request, user: User, data: Mapping) -> None:
    serializer = ChangePasswordSerializer(user, data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    auth_login(request, user)


def add_products_to_favourites(user: User, products_ids: List[int]) -> None:
    FavouriteProduct.objects.bulk_create([FavouriteProduct(user=user, product_id=product_id)
                                          for product_id in products_ids], ignore_conflicts=True)


def remove_product_from_favourites(user: User, product_id: int) -> None:
    FavouriteProduct.objects.filter(user=user, product_id=product_id).delete()


def clear_favourites(user: User) -> None:
    user.favourites.all().delete()


def login(request: Request) -> None:
    form = AuthenticationForm(request, request.data)

    if form.is_valid():
        user = form.get_user()

        if hasattr(user, "client"):
            client = Client.objects.get(account=user)

            if client.is_expired:
                raise PermissionDenied("Истек срок действия аккаунта")

            device_verified = set_or_verify_user_device(client, request)

            if not device_verified:
                email_subject = "Попытка входа в аккаунт с другим устройством"
                email_content = (f'<b>Пользователь: </b>{client.fullname}<br><b>Номер телефона: </b>{user.username}<br>'
                                 f'<b>ИП: </b>{client.company_name}')
                recipient = Contact.objects.get(type="email").contact
                send_mail(email_subject, email_content, EMAIL_HOST_USER, [recipient], fail_silently=False,
                          html_message=email_content)
                raise PermissionDenied("Устройство не верифицировано")

            auth_login(request, user)

            first_session = None
            for session in Session.objects.all():
                if session.get_decoded().get(SESSION_KEY) == request.session[SESSION_KEY]:
                    if not first_session:
                        first_session = session
                    else:
                        first_session.delete()
                        break
        else:
            auth_login(request, user)

        if request.data["favourite_products"]:
            add_products_to_favourites(user, request.data["favourite_products"])
    else:
        raise ValidationError(dict(form.errors))


def change_user_fullname(user: User, first_name: str, last_name: str) -> None:
    user.client.fullname = first_name + " " + last_name
    user.client.save(update_fields=["fullname"])


def add_client(data: Mapping) -> int:
    serializer = ClientFormSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save().id


def edit_client(client_id: int, data: Mapping) -> int:
    client = get_object_or_404(Client, id=client_id)
    serializer = ClientFormSerializer(client, data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save().id


def delete_client(client_id: int) -> None:
    User.objects.filter(client__id=client_id).delete()


def get_client(client_id: int) -> ClientSerializer:
    client = Client.objects.filter(id=client_id).first()
    return ClientSerializer(client)


def get_clients(last_obj_id: int) -> ClientSerializer:
    if int(last_obj_id) == 0:
        clients = Client.objects.all().order_by("-id")[:40]
    else:
        clients = Client.objects.filter(id__lt=int(last_obj_id)).order_by("-id")[:40]

    return ClientSerializer(clients, many=True)


def set_or_verify_user_device(client: Client, request: Request) -> bool:
    if client.device1:
        if client.device1 != request.META['HTTP_USER_AGENT']:
            if client.device2:
                return client.device2 == request.META['HTTP_USER_AGENT']
            else:
                client.device2 = request.META['HTTP_USER_AGENT']
                client.save(update_fields=["device2"])
    else:
        client.device1 = request.META['HTTP_USER_AGENT']
        client.save(update_fields=["device1"])

    return True
