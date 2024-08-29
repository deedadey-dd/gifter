# store/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from .models import Vendor


class VendorBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            vendor = Vendor.objects.get(username=username)
        except Vendor.DoesNotExist:
            try:
                vendor = Vendor.objects.get(email=username)
            except Vendor.DoesNotExist:
                return None

        if vendor.check_password(password):
            return vendor
        return None
