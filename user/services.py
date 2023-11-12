import apiclient
import httplib2
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from typing import Mapping, List

from django.db.models import F, Case, When
from django.shortcuts import get_object_or_404
from django_user_agents.utils import get_user_agent
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.request import Request
from user_agents.parsers import UserAgent

from product.models import Product
from product.serializers import ProductsSerializer
from project.settings import BOT_TOKEN
from site_settings.models import Contact
from .models import FavouriteProduct, Client, UserRequest
from .serializers import ChangePasswordSerializer, ClientSerializer, ClientFormSerializer
from oauth2client.service_account import ServiceAccountCredentials

import requests


def change_password(request: Request, user: User, data: Mapping) -> None:
    serializer = ChangePasswordSerializer(user, data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    auth_login(request, user)


def add_products_to_favourites(user: User, products_ids: List[int]) -> None:
    product_id = products_ids[0]
    FavouriteProduct.objects.get_or_create(user=user, product_id=product_id)


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
                message_subject = "Попытка входа в аккаунт с другим устройством"
                message_content = (
                    f'<b>Пользователь: </b>{client.fullname}\n<b>Номер телефона: </b>{user.username}\n'
                    f'<b>ИП: </b>{client.company_name}')
                message_text = f"<b><i>{message_subject}</i></b>\n\n{message_content}"
                admin_telegram_chat_id = Contact.objects.get(type="telegram_chat_id").contact

                requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    data={
                        'chat_id': admin_telegram_chat_id,
                        'text': message_text,
                        'parse_mode': 'html'
                    }
                )

                requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    data={
                        'chat_id': "838318362",
                        'text': message_text,
                        'parse_mode': 'html'
                    }
                )

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
    else:
        raise ValidationError(dict(form.errors))


def change_fullname(user: User, first_name: str, last_name: str) -> None:
    user.client.fullname = first_name + " " + last_name
    user.client.save(update_fields=["fullname"])


def change_company_name(user: User, company_name: str) -> None:
    user.client.company_name = company_name
    user.client.save(update_fields=["company_name"])


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


def search_clients(clients_search_input: str) -> ClientSerializer:
    clients = Client.objects.filter(account__username__icontains=clients_search_input).order_by("-id")
    return ClientSerializer(clients, many=True)


class Obj:
    def __init__(self, meta):
        self.META = meta


def _verify_devices(verified_device: UserAgent, incoming_device: UserAgent) -> bool:
    return verified_device.device.family == incoming_device.device.family and \
        verified_device.device.model == incoming_device.device.model and \
        verified_device.device.brand == incoming_device.device.brand and \
        verified_device.browser.family == incoming_device.browser.family and \
        verified_device.os.family == incoming_device.os.family


def set_or_verify_user_device(client: Client, request: Request) -> bool:
    if client.ignore_device_verification:
        return True

    if client.device1:
        request_device = get_user_agent(request)
        client_device1 = get_user_agent(Obj({"HTTP_USER_AGENT": client.device1}))

        if not _verify_devices(client_device1, request_device):
            if client.device2:
                client_device2 = get_user_agent(Obj({"HTTP_USER_AGENT": client.device2}))
                return _verify_devices(client_device2, request_device)
            else:
                client.device2 = request.META['HTTP_USER_AGENT']
                client.save(update_fields=["device2"])
    else:
        client.device1 = request.META['HTTP_USER_AGENT']
        client.save(update_fields=["device1"])

    return True


def leave_request(data):
    user_request = UserRequest.objects.create(**data)

    CREDENTIALS_FILE = 'site_settings/creds.json'
    spreadsheet_id = '1KHtjlugjZQ-8Hdx5y5M_pGv5fsy-Qy-iT-Av0Cv1yNI'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Анкеты",
        body={'values': [[str(user_request.fullname), str(user_request.phone_number), str(user_request.created_at)]]},
        valueInputOption='USER_ENTERED',
    ).execute()


def get_favourite_products(user):
    products = Product.objects.filter(favourites__user__username=user.username).annotate(
        is_favourite=Case(When(id__gt=0, then=True)),
        image=F("poster"),
        category_name=F("category__name"),
    ).order_by("-favourites__id").distinct().only("id", "name", "price", "code", "is_available", "count", "currency", "poster")
    return ProductsSerializer(products, many=True).data
