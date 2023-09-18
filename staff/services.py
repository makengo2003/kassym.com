import json

import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from base_object_presenter.services import BaseServicesPresenter
from .models import StaffModelPresenter


class StaffServicesPresenter(BaseServicesPresenter):
    def __init__(self):
        self.model_presenter = StaffModelPresenter()
        super().__init__()

        self.CREDENTIALS_FILE = 'site_settings/creds.json'
        self.spreadsheet_id = '1PXHIvivknTpSZhnaL0DavX8RFmlu0FRvHh1wxres2HA'

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)

    def add_order(self, data):
        data["product"] = json.loads(data["product"])

        self.orders_sheet_update(data)
        self.company_names_sheet_update(data)

    def orders_sheet_update(self, data):
        new_product_code = data["product"]["name"]
        new_product_count = data["count"]

        # Получаем данные из таблицы
        response = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='Заказы'  # Укажите имя листа, где находятся данные
        ).execute()

        values = response.get('values', [])

        if not values:
            print('Таблица пуста.')
        else:
            product_codes = [row[0] for row in values]  # Предполагается, что product_code находится в первом столбце

            if new_product_code in product_codes:
                # Если код продукта уже существует, обновляем значение product_count
                row_index = product_codes.index(new_product_code)
                print(values[row_index][1])
                update_range = f'A{row_index + 1}:B{row_index + 1}'  # Обновляем только строку, где совпал код продукта
                update_values = [[new_product_code, new_product_count + int(values[row_index][1])]]
                request_body = {'values': update_values}

                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=update_range,
                    body=request_body,
                    valueInputOption='RAW'
                ).execute()
            else:
                # Если код продукта не существует, добавляем новую запись в конец таблицы
                append_values = [[new_product_code, new_product_count]]

                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range='Заказы',  # Укажите имя листа, где добавлять данные
                    body={'values': append_values},
                    valueInputOption='RAW',
                ).execute()

    def company_names_sheet_update(self, data):
        company_name = data["company_name"]
        new_product_code = data["product"]["name"]
        new_product_count = data["count"]

        # Получаем данные из таблицы
        response = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='ИП'  # Укажите имя листа, где находятся данные
        ).execute()

        values = response.get('values', [])

        if not values:
            print('Таблица пуста.')
        else:
            company_names = [row[0] for row in values]  # Предполагается, что company_name находится в первом столбце

            if company_name in company_names:
                index = company_names.index(company_name)
                updated = False

                for i in range(index, len(company_names)):
                    if company_names[i] == company_name:
                        if values[i][1] == new_product_code:
                            values[i][2] = int(values[i][2]) + new_product_count
                            updated = True
                            break

                if not updated:
                    values.append([company_name, new_product_code, new_product_count])

                for i in range(1, len(company_names)):
                    values[i][2] = int(values[i][2])

                update_range = 'ИП!A1'
                request_body = {'values': values}

                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=update_range,
                    body=request_body,
                    valueInputOption='RAW'
                ).execute()
            else:
                # Если company_name не существует, добавляем новую запись
                append_values = [[company_name, new_product_code, new_product_count]]
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range='ИП',  # Укажите имя листа, где добавлять данные
                    body={'values': append_values},
                    valueInputOption='RAW',
                ).execute()
