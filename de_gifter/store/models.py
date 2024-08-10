import random

from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
import string
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name


class Vendor(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('recently_seen', 'Recently Seen'),
    ]

    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField()
    logo = models.ImageField(upload_to='uploads/vendors/', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recently_seen')
    last_seen = models.DateTimeField(default=timezone.now)
    verification = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    location = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)
    phone_confirmed = models.BooleanField(default=False)
    phone_confirmation_pin = models.CharField(max_length=6, blank=True, null=True)
    fee_percentage = models.FloatField(default=5.0)  # Fee percentage for each transaction

    def generate_confirmation_pin(self):
        self.phone_confirmation_pin = ''.join(random.choices(string.digits, k=6))
        self.save()

    def save(self, *args, **kwargs):
        if self.last_seen:
            now = timezone.now()
            if now - self.last_seen < timezone.timedelta(days=45):
                self.status = 'active'
            elif now - self.last_seen > timezone.timedelta(days=90):
                self.status = 'inactive'
            else:
                self.status = 'recently_seen'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):

    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Used', 'Used'),
        ('Refurbished', 'Refurbished'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='uploads/products/', null=True, blank=True)
    popularity_count = models.IntegerField(default=0)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='New')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_amount = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


def process_transaction(product_id, amount_paid):
    product = get_object_or_404(Product, id=product_id)
    vendor = product.vendor
    fee_percentage = vendor.fee_percentage
    fee_amount = (amount_paid * fee_percentage) / 100
    vendor_earnings = amount_paid - fee_amount

    # Process payment and update vendor earnings
    # e.g., update the vendor's earnings in the database or perform other actions

    return vendor_earnings, fee_amount

