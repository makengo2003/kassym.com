"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from project import settings

urlpatterns = [
    path("", include("pages.urls")),
    path('djadmin/', admin.site.urls),
    path('api/site_settings/', include("site_settings.urls")),
    path('api/category/', include("category.urls")),
    path('api/product/', include("product.urls")),
    path('api/user/', include("user.urls")),
    path('api/course/', include("course.urls")),
    path('api/staff/', include("staff.urls")),
    path('api/cart/', include("cart.urls")),
    path('api/order/', include("order.urls")),
    path('api/change_time/', include("change_time.urls")),
    path('api/purchase/', include("purchase.urls")),
    path('api/sorting/', include("sorting.urls")),
    path('api/delivering/', include("delivering.urls")),
    path('api/supplier/', include("supplier.urls")),
    path('api/expense/', include("expense.urls")),
    path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
