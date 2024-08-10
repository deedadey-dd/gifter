from django.contrib import admin
from .models import Category, Vendor, Product, ProductImage, Order, OrderItem

admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderItem)
