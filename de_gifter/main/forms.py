from django import forms
from .models import Item, ItemImage, Wishlist, WishlistItem, Vendor, User
from django.contrib.auth.forms import UserCreationForm


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'vendor', 'category']


class UserLoginForm(forms.Form):
    identifier = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=20)
    profile_picture = forms.ImageField(required=False)
    # cash_on_hand = forms.FloatField(required=False, initial=0.00)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'phone_number', 'profile_picture', 'password1', 'password2']


class PhoneConfirmationForm(forms.Form):
    pin = forms.CharField(max_length=6, required=True)


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['title', 'description', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(
                format='%d-%m-%Y',
                attrs={'type': 'date'}
            ),
        }


class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['item_name', 'item_description', 'item_price', 'item_image_url']


class VendorRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20)
    logo = forms.ImageField(required=False)
    location = forms.CharField(max_length=255)

    class Meta:
        model = Vendor
        fields = ['name', 'description', 'logo', 'phone_number', 'location', 'email']


class StoreItemSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False)


class CustomItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['item_name', 'item_description', 'item_price', 'item_image_url']


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image_url']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'multiple': False}),
        }


class ContributionForm(forms.Form):
    name = forms.CharField(max_length=150, required=False, help_text='Your name (optional)')
    phone = forms.CharField(max_length=20, required=False, help_text='Your phone number (optional)')
    amount = forms.FloatField()
    message = forms.CharField(widget=forms.Textarea, required=False)
