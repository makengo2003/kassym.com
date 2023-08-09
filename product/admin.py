from django.contrib import admin
from .models import Product, ProductImage, ProductOption, ProductOptionValue

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductOption)
admin.site.register(ProductOptionValue)
