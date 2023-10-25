from django.contrib import admin
from user.models import FavouriteProduct, Client, UserRequest

admin.site.register(FavouriteProduct)
admin.site.register(Client)
admin.site.register(UserRequest)
