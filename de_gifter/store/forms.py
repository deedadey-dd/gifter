# store/forms.py

from django import forms
from .models import Product, Order, OrderItem, ShippingDetails, Vendor  # Adjust import based on your project structure


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'vendor', 'category', 'image', 'condition']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['total_amount', 'status']
        widgets = {
            'status': forms.Select(choices=Order.STATUS_CHOICES),
        }

    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method not in ['Credit Card', 'PayPal', 'Bank Transfer']:
            raise forms.ValidationError("Invalid payment method")
        return payment_method


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class ShippingDetailsForm(forms.ModelForm):
    class Meta:
        model = ShippingDetails
        fields = ['address', 'city', 'state', 'postal_code', 'country', 'phone_number', 'shipping_method', 'tracking_number']


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'description', 'logo', 'phone_number', 'location']
