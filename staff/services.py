import csv
import json
import os

import httplib2
import apiclient.discovery
from dateutil.relativedelta import relativedelta
from oauth2client.service_account import ServiceAccountCredentials

from base_object_presenter.services import BaseServicesPresenter
from product.models import Product
from project import settings
from project.utils import datetime_now
from .models import StaffModelPresenter


class StaffServicesPresenter(BaseServicesPresenter):
    def __init__(self):
        self.model_presenter = StaffModelPresenter()
        super().__init__()

        self.CREDENTIALS_FILE = 'site_settings/creds.json'
        self.spreadsheet_id = '13WcrMVYLQsbqy4uF9DRsp_mliCRTS_T0_3CI2IG7g4s'

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)

    def add_order(self, data):
        data["product"] = json.loads(data["product"])

        company_name = data["company_name"]
        product_count = data["count"]
        product_name = data["product"]["name"]
        product_code = data["product"]["code"]
        product_image = f'= IMAGE("https://kassym.com/{data["product"]["image"]}"; 2)'
        product_price = str(data["product"]["price"])
        order_date = data["date"]

        if data["product"]["category_name"] == "Товары со склада":
            if settings.DEBUG:
                sheetname = "Заказы (Китай) (копия)"
            else:
                sheetname = "Заказы (Китай)"
        else:
            if settings.DEBUG:
                sheetname = "Заказы (Базар) (копия)"
            else:
                sheetname = "Заказы (Базар)"

        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=sheetname,
            body={'values': [[
                company_name,
                product_count,
                product_name,
                product_code,
                product_image,
                product_price,
                order_date,
                "."
            ]]},
            valueInputOption='USER_ENTERED',
        ).execute()

        self.update_product_count(data["product"]["id"], data["count"])
        self.save_backup(sheetname)

    def save_backup(self, sheetname):
        today = datetime_now().date()
        csv_file = f"../sheets/{sheetname}-{today}.csv"

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)

            response = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=sheetname,
                valueRenderOption='FORMULA'
            ).execute()

            for row in response.get('values', []):
                writer.writerow(row)

        os.system(f'rm "../sheets/{sheetname}-{today - relativedelta(days=3)}.csv"')

    def update_product_count(self, product_id, count):
        product = Product.objects.filter(id=product_id).only("count").first()

        count = product.count - count
        if count < 0:
            count = 0

        Product.objects.filter(id=product_id).update(count=count)
