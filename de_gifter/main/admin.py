# main/admin.py

from django.contrib import admin
from .models import User, Vendor, Category, Item, ItemImage, Wishlist, WishlistItem, Contribution

admin.site.register(User)
admin.site.register(Vendor)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Contribution)


# Check if the model is already registered
if not admin.site.is_registered(Vendor):
    @admin.register(Vendor)
    class VendorAdmin(admin.ModelAdmin):
        list_display = ('name', 'status', 'last_seen', 'verification', 'location')
        search_fields = ('name', 'status', 'verification', 'location')
        list_filter = ('status', 'verification', 'location')

