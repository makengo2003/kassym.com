from django.contrib import admin
from user.models import FavouriteProduct, Client, UserRequest, MyCard

admin.site.register(FavouriteProduct)
admin.site.register(MyCard)
admin.site.register(Client)
admin.site.register(UserRequest)
