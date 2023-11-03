from django.http import FileResponse
from django.shortcuts import render, redirect

from project.utils import check_account_expiration
from site_settings import services as site_settings_services
from django.views.decorators.cache import never_cache
from project.settings import MAIN_CATEGORY_ID
from course import services as course_services
from product import services as product_services
from user import services as user_services
import random


@never_cache
def search_page_view(request):
    products_count = product_services.get_many(request.user, request.GET)["count"]
    return render(request, "v2/search_page.html", {"count": products_count})


@never_cache
def main_page_view(request):
    products = product_services.get_top_5_products_of_each_category(request.user)
    random.shuffle(products)
    return render(request, "v2/main_page.html", {"products": products})


@never_cache
@check_account_expiration()
def favourites_page_view(request):
    if request.user.is_authenticated:
        products = user_services.get_favourite_products(request.user)
        return render(request, "v2/wishlist_page.html", {"products": products})
    return redirect("/")


@never_cache
@check_account_expiration()
def products_page_view(request):
    if request.user.is_authenticated:
        selected_category_id = int(request.GET.get("category_id"))
        category_info = product_services.get_category_info(selected_category_id)

        return render(request, "v2/products_page.html", {
            "min_price": category_info["min_price"],
            "max_price": category_info["max_price"],
            "count": category_info["count"],

            "selected_category_id": selected_category_id,
            "selected_ordering": request.GET.get("ordering", "-id"),
            "selected_min_price": request.GET.get("min_price", category_info["min_price"]),
            "selected_max_price": request.GET.get("max_price", category_info["max_price"]),
            "selected_page": request.GET.get("page", 1)
        })
    return redirect("/")


@never_cache
@check_account_expiration()
def product_page_view(request):
    if request.user.is_authenticated:
        product = product_services.get_product(request.user, request.GET.get("product_id", 0)).data
        products = product_services.get_products(request.user, products_filtration={"category_id": product["category_id"]}, products_order_by="-id").data

        if "favourites" in request.META.get("HTTP_REFERER", ""):
            label = "Избранные"
            url = request.META["HTTP_REFERER"]
        elif "search_result" in request.META.get("HTTP_REFERER", ""):
            label = "Результаты поиска"
            url = request.META["HTTP_REFERER"]
        elif "products" in request.META.get("HTTP_REFERER", ""):
            label = product["category_name"]
            url = request.META["HTTP_REFERER"]
        else:
            label = product["category_name"]
            url = "/products/?category_id=" + str(product["category_id"])

        go_back = {
            "label": label,
            "url": url
        }
        context = {"product": product, "products": products, "go_back": go_back}

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, "v2/product.html", context)
        return render(request, "v2/product_page.html", context)
    return redirect("/")


@never_cache
@check_account_expiration()
def admin_page_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return render(request, "pages/admin_page.html", {"MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})
    return redirect("/profile/")


@never_cache
@check_account_expiration()
def profile_page_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect("/admin/")
        return render(request, "pages/profile_page.html")
    return redirect("/")


@never_cache
def about_us_view(request):
    return render(request, "pages/about_us_page.html", {"about_us": site_settings_services.get_about_us_text()})


@never_cache
def guarantee_view(request):
    return FileResponse(site_settings_services.get_guarantee_file())


@never_cache
@check_account_expiration()
def courses_page_view(request):
    if request.user.is_authenticated:
        language = request.GET.get("lang", "kz")
        courses = course_services.get_courses_page(language)
        return render(request, "v2/courses_page.html", {"courses": courses})
    return redirect("/")


@never_cache
@check_account_expiration()
def lesson_page_view(request):
    if request.user.is_authenticated:
        lesson_id = request.GET.get("id", 0)
        course, lessons, lesson = course_services.get_lesson_page(lesson_id)
        return render(request, "v2/lesson_page.html", {"course": course, "lessons": lessons, "lesson": lesson})
    return redirect("/")
