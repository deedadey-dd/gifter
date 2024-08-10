# main/admin.py

from django.contrib import admin
from .models import User, Item, ItemImage, Wishlist, WishlistItem, Contribution

admin.site.register(User)
admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Contribution)
