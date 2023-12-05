import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from delivering.consumers import DeliveringConsumer
from order.consumers import OrderConsumer
from purchase.consumers import PurchaseConsumer
from sorting.consumers import SortingConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter([
                re_path(r"ws/order/", OrderConsumer.as_asgi()),
                re_path(r"ws/purchase/", PurchaseConsumer.as_asgi()),
                re_path(r"ws/sorting/", SortingConsumer.as_asgi()),
                re_path(r"ws/delivering/", DeliveringConsumer.as_asgi()),
            ])
        ),
    }
)
