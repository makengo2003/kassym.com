from django.http import FileResponse
from django.shortcuts import render, redirect

from project.utils import check_account_expiration
from site_settings import services as site_settings_services
from django.views.decorators.cache import never_cache
from project.settings import MAIN_CATEGORY_ID
from course import services as course_services


@never_cache
def search_result_page_view(request):
    return render(request, "pages/search_result_page.html", {"search_input": request.GET.get("search_input"), "MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})


@never_cache
def main_page_view(request):
    return render(request, "pages/main_page.html")


@never_cache
@check_account_expiration()
def favourites_page_view(request):
    if request.user.is_authenticated:
        return render(request, "pages/favourites_page.html", {"MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})
    return redirect("/")


@never_cache
@check_account_expiration()
def products_page_view(request):
    if request.user.is_authenticated:
        return render(request, "pages/products_page.html", {"MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})
    return redirect("/")


@never_cache
@check_account_expiration()
def product_page_view(request):
    if request.user.is_authenticated:
        return render(request, "pages/product_page.html", {"MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})
    return redirect("/")


@never_cache
@check_account_expiration()
def admin_page_view(request):
    if request.user.is_superuser:
        return render(request, "pages/admin_page.html", {"MAIN_CATEGORY_ID": MAIN_CATEGORY_ID})
    return redirect("/")


@never_cache
@check_account_expiration()
def profile_page_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
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
        return render(request, "pages/courses_page.html", {"courses": courses})
    return redirect("/")


@never_cache
@check_account_expiration()
def lesson_page_view(request):
    if request.user.is_authenticated:
        lesson_id = request.GET.get("id", 0)
        course, lessons, lesson = course_services.get_lesson_page(lesson_id)
        return render(request, "pages/lesson_page.html", {"course": course, "lessons": lessons, "lesson": lesson})
    return redirect("/")
