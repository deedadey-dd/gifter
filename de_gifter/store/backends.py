# store/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Vendor


class VendorBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            vendor = Vendor.objects.get(email=email)
            if vendor.check_password(password):
                return vendor
        except Vendor.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Vendor.objects.get(pk=user_id)
        except Vendor.DoesNotExist:
            return None
