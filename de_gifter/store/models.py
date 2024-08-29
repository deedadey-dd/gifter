import random
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
import string
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name


class VendorManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Uses AbstractBaseUser's set_password method
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class Vendor(AbstractBaseUser, PermissionsMixin):
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

    username = models.CharField(max_length=150, unique=True)
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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = VendorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', default='uncategorized', null=True)
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
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
    ]
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


class ShippingDetails(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    shipping_method = models.CharField(max_length=100, choices=[('Standard', 'Standard'), ('Express', 'Express')])
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Shipping details for Order {self.order.id}"

