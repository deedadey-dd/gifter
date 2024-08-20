# main/models.py

import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(upload_to='uploads/profiles/', null=True, blank=True)
    cash_on_hand = models.FloatField(default=0.00)
    email_confirmed = models.BooleanField(default=False)
    phone_confirmed = models.BooleanField(default=False)
    phone_confirmation_pin = models.CharField(max_length=6, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Add a unique related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Add a unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def generate_confirmation_pin(self):
        self.phone_confirmation_pin = ''.join(random.choices(string.digits, k=6))
        self.save()

    def __str__(self):
        return self.username


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    added_to_wishlist_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image_url = models.ImageField(upload_to='uploads/items/')

    def __str__(self):
        return f"Image for {self.item.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=240, blank=True, null=True)
    expiry_date = models.DateField()
    extra_cash = models.FloatField(default=0.00)

    def __str__(self):
        return self.title

    def calculate_extra_cash(self):
        """Calculate the extra cash from all wishlist items."""
        total_contributions = sum(
            contribution.amount for item in self.items.all() for contribution in item.contributions.all())
        total_item_prices = sum(item.item_price for item in self.items.all())
        self.extra_cash = total_contributions - total_item_prices
        if self.extra_cash < 0:
            self.extra_cash = 0.0
        self.save()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='wishlist_items')
    item_name = models.CharField(max_length=120)
    item_description = models.TextField(max_length=240, blank=True, null=True)
    item_price = models.FloatField()
    item_image = models.ImageField(upload_to='uploads/items/', null=True, blank=True)  # This field is for image uploads
    status = models.CharField(max_length=20, default='Pending')
    amount_paid = models.FloatField(default=0.0)
    item_image_url = models.URLField(max_length=150, null=True, blank=True)  # Optional URL field

    def __str__(self):
        return self.item_name


class Contribution(models.Model):
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, related_name='contributions')
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    amount = models.FloatField()
    message = models.TextField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.amount}"
