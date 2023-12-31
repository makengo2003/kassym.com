from base_object_presenter.urls import BaseURLsPresenter
from .views import PurchaseViewsPresenter


class PurchaseURLsPresenter(BaseURLsPresenter):
    views = PurchaseViewsPresenter()
    urls = ["get_purchases", "get_purchases_counts", "make", "save_is_being_considered_purchases",
            "get_is_being_considered_purchase", "get_purchase_comments", "get_purchase_for_manager",
            "get_purchased_product_orders"]


urlpatterns = PurchaseURLsPresenter().get_urlpatterns()
