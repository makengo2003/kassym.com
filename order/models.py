import time

import PyPDF2
import apiclient
import httplib2
from bs4 import BeautifulSoup
import requests

from django.db import models
from oauth2client.service_account import ServiceAccountCredentials

from base_object_presenter.models import BaseModelPresenter
from django.contrib.auth.models import User

from cart.models import CartItem
from project import settings
from project.utils import datetime_now


class Order(models.Model):
    created_at = models.DateField(default=datetime_now, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deliveries_qr_code = models.FileField(upload_to="deliveries_qr_code/")
    selection_sheet_file = models.FileField(upload_to="selection_sheet_files/")
    is_express = models.BooleanField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    paid_check_file = models.FileField(upload_to="paid_check_files/")
    one_file_products_qr_codes = models.FileField(upload_to="one_file_products_qr_codes/", null=True)
    ruble_rate = models.FloatField()
    total_products_count = models.PositiveIntegerField()
    service_price_per_count = models.PositiveIntegerField()
    express_price_per_count = models.PositiveIntegerField()
    total_service_price = models.PositiveIntegerField()
    total_products_price = models.PositiveIntegerField()
    total_sum_in_tenge = models.FloatField()
    total_sum_in_ruble = models.PositiveIntegerField()
    specific_product = models.BooleanField()
    price_for_specific_product = models.PositiveIntegerField()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    qr_code = models.FileField(upload_to="products_qr_code/")
    product_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()


class OrderModelPresenter(BaseModelPresenter):
    model = Order

    def __init__(self):
        self.CREDENTIALS_FILE = 'site_settings/creds.json'
        self.spreadsheet_id = '13WcrMVYLQsbqy4uF9DRsp_mliCRTS_T0_3CI2IG7g4s'

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)

    @staticmethod
    def get_object_add_form_serializer_fields():
        return ["is_express", "deliveries_qr_code", "selection_sheet_file", "comments", "paid_check_file"]

    def calculate(self, user, data, cart_items=None):
        if not cart_items:
            cart_items = CartItem.objects.select_related("product").filter(user=user)

        total_products_count = 0
        total_products_price = 0
        total_service_price = 0
        specific_product = False
        price_for_specific_product = 100
        specific_products_count = 0

        for cart_item in cart_items:
            total_products_price += cart_item.count * cart_item.product.price
            total_products_count += cart_item.count

            if cart_item.product_id == 7810 or cart_item.product_id == 714:
                total_service_price += price_for_specific_product * cart_item.count
                specific_product = True
                specific_products_count += cart_item.count

        service_price_per_count = 50
        express_price_per_count = 150
        total_service_price += service_price_per_count * (total_products_count - specific_products_count)

        is_express = data.get("is_express", False)
        if (type(is_express) == str and is_express == "true") or (type(is_express) == bool and is_express is True):
            total_service_price += express_price_per_count * total_products_count

        ruble_rate = self.get_ruble_rate()
        total_sum_in_ruble = total_products_price + total_service_price
        total_sum_in_tenge = total_sum_in_ruble * ruble_rate

        return {
            "ruble_rate": ruble_rate,
            "total_products_count": total_products_count,
            "service_price_per_count": service_price_per_count,
            "express_price_per_count": express_price_per_count,
            "total_service_price": total_service_price,
            "total_products_price": total_products_price,
            "total_sum_in_tenge": round(total_sum_in_tenge, 2),
            "total_sum_in_ruble": total_sum_in_ruble,
            "specific_product": specific_product,
            "price_for_specific_product": price_for_specific_product
        }

    def object_add_form_serializer_create(self, validated_data):
        request_user = getattr(settings, 'request_user', None)
        cart_items = CartItem.objects.select_related("product").filter(user=request_user)

        order_items = []
        qr_codes = validated_data.pop("files")
        i = 0
        for qr_code in qr_codes:
            if qr_code.startswith("cart_item_qr_code_"):
                cart_item = cart_items[i]
                total_price = cart_item.count * cart_item.product.price
                order_items.append(
                    OrderItem(qr_code=qr_codes[qr_code], count=cart_item.count, product_id=cart_item.product_id,
                              product_price=cart_item.product.price, total_price=total_price))
                i += 1

        calculated_prices = self.calculate(request_user, {"is_express": validated_data.get("is_express")},
                                           cart_items=cart_items)
        deliveries_qr_code = validated_data.pop("deliveries_qr_code")
        selection_sheet_file = validated_data.pop("selection_sheet_file")
        paid_check_file = validated_data.pop("paid_check_file")
        one_file_products_qr_codes = self.get_one_file_products_qr_codes(request_user,
                                                                         [order_items_obj.qr_code for order_items_obj in
                                                                          order_items])

        order = Order.objects.create(user=request_user, deliveries_qr_code=deliveries_qr_code,
                                     selection_sheet_file=selection_sheet_file, paid_check_file=paid_check_file,
                                     one_file_products_qr_codes=one_file_products_qr_codes,
                                     **validated_data, **calculated_prices)

        for order_items_obj in order_items:
            order_items_obj.order = order

        OrderItem.objects.bulk_create(order_items)
        CartItem.objects.filter(user=request_user).delete()

        self.add_to_google_sheets(request_user, order, order_items)
        return order

    def get_ruble_rate(self):
        response = requests.get("https://mig.kz/api/v1/gadget/html")
        soup = BeautifulSoup(response.text, 'html.parser')
        rub_row = soup.find('td', class_='currency', text='RUB').find_parent('tr')
        return float(rub_row.find('td', class_='sell delta-neutral').text) + 0.5

    def get_one_file_products_qr_codes(self, user, qr_codes):
        pdf_merger = PyPDF2.PdfMerger()

        for pdf_file in qr_codes:
            pdf_merger.append(pdf_file)

        output_pdf = f"../media/one_file_products_qr_codes/merged_qr_codes_{user.username}_{time.time()}.pdf"

        with open(output_pdf, "wb") as output_file:
            pdf_merger.write(output_file)

        pdf_merger.close()

        return output_pdf

    def add_to_google_sheets(self, user, order, order_items):
        spreadsheet_id = "1jNPKGAV-zvcgsA830Ts9u-L6DVIgIKBhX0-PCBXFY5E"

        manager_sheetname = "Менеджер"
        china_buyer_sheetname = "Закупщик Китай"
        market_buyer_sheetname = "Закупщик Базар"

        manager_values = []
        china_values = []
        market_values = []

        for (i, order_item) in enumerate(order_items):
            if hasattr(user, "client"):
                company_name = user.client.company_name
            else:
                company_name = "Admin"

            username = f'"{user.username}"'
            comments = order.comments
            deliveries_qr_code = f'= ГИПЕРССЫЛКА("https://kassym.com{order.deliveries_qr_code.url}")'
            selection_sheet_file = f'= ГИПЕРССЫЛКА("https://kassym.com{order.selection_sheet_file.url}")'
            paid_check_file = f'= ГИПЕРССЫЛКА("https://kassym.com{order.paid_check_file.url}")'
            one_file_products_qr_codes = f'= ГИПЕРССЫЛКА("https://kassym.com{order.one_file_products_qr_codes.url}")'

            row = [
                company_name,
                order_item.product.name,
                order_item.count,
                f'= IMAGE("https://kassym.com{order_item.product.poster.url}"; 2)',
                order_item.product.price,
                ".",
                f'"{order_item.product.vendor_number}"',
                comments,
                username,
                ".",
                f'= ГИПЕРССЫЛКА("https://kassym.com{order_item.qr_code.url}")',
                False,
                one_file_products_qr_codes,
                deliveries_qr_code,
                selection_sheet_file,
            ]

            manager_values.append(row + [paid_check_file])
            if order_item.product.category_id == 7:
                china_values.append(row)
            else:
                market_values.append(row)

        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=manager_sheetname,
            body={'values': manager_values},
            valueInputOption='USER_ENTERED',
        ).execute()

        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=market_buyer_sheetname,
            body={'values': market_values},
            valueInputOption='USER_ENTERED',
        ).execute()

        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=china_buyer_sheetname,
            body={'values': china_values},
            valueInputOption='USER_ENTERED',
        ).execute()
