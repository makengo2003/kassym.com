import json

import requests
from bs4 import BeautifulSoup

from cart.models import CartItem
from order.models import Order


def calculate(user, data, cart_items=None):
    if not cart_items:
        cart_items = CartItem.objects.select_related("product").filter(user=user)

    total_products_count = 0
    total_products_price = 0
    total_service_price = 0
    specific_product = False
    price_for_specific_product = 100
    specific_products_count = 0
    products_ids = {}

    check_defects_list = data["check_defects"]
    if type(check_defects_list) == str:
        check_defects_list = json.loads(check_defects_list)

    with_gift_list = data["with_gift"]
    if type(with_gift_list) == str:
        with_gift_list = json.loads(with_gift_list)

    for cart_item in cart_items:
        total_products_price += cart_item.count * (cart_item.product.price - cart_item.product.price * cart_item.product.discount_percentage / 100)
        total_products_count += cart_item.count

        if cart_item.product_id in [7810, 714, 8433, 8432, 8431, 8429, 8428, 8424, 8423, 8413]:
            if cart_item.product_id in [8433, 8432, 8431, 8429, 8428, 8424, 8423, 8413]:
                _price_for_specific_product = 150
            else:
                _price_for_specific_product = 100

            total_service_price += _price_for_specific_product * cart_item.count
            specific_product = True
            specific_products_count += cart_item.count

        products_ids[cart_item.product_id] = products_ids.get(cart_item.product_id, 0) + cart_item.count

        check_defects = check_defects_list.get(str(cart_item.id), False)
        if check_defects:
            total_service_price += 30 * cart_item.count

        with_gift = with_gift_list.get(str(cart_item.id), False)
        if with_gift:
            total_service_price += 50 * cart_item.count

    service_price_per_count = 50
    express_price_per_count = 150
    total_service_price += service_price_per_count * (total_products_count - specific_products_count)

    is_express = data.get("is_express", False)
    if (type(is_express) == str and is_express == "true") or (type(is_express) == bool and is_express is True):
        total_service_price += express_price_per_count * total_products_count

    ruble_rate = get_ruble_rate()
    total_sum_in_ruble = total_products_price + total_service_price
    total_sum_in_tenge = total_sum_in_ruble * ruble_rate

    last_order = Order.objects.filter(user=user).prefetch_related("order_items__product").last()
    found_count = 0

    if last_order:
        for order_item in last_order.order_items.all():
            if order_item.product.id in products_ids:
                found_count += order_item.count == products_ids[order_item.product.id]

    return {
        "is_same_with_last_order": len(products_ids) == found_count,
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


def get_ruble_rate():
    response = requests.get("https://mig.kz/api/v1/gadget/html")
    soup = BeautifulSoup(response.text, 'html.parser')
    rub_row = soup.find('td', class_='currency', text='RUB').find_parent('tr')
    return float(rub_row.find('td', class_='sell').text) + 0.5


def get_order(user, order_id):
    order = Order.objects.filter(user=user, id=order_id).prefetch_related("reports", "order_items", "order_items__purchases").first()
    return order
