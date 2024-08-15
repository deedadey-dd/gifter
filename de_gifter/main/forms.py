from django import forms
from .models import Item, ItemImage, Wishlist, WishlistItem, User
from store.models import Vendor
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django_countries.widgets import CountrySelectWidget
from country_dialcode.widgets import CountryDialcodeSelectWidget


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price']


class UserLoginForm(forms.Form):
    identifier = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
#     name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     country_code = CountryField().formfield(
#         widget=CountrySelectWidget(attrs={'class': 'form-control'})
#     )
#     phone_number = forms.CharField(
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter your phone number',
#             'type': 'tel'
#         })
#     )
#
#     profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
#     user_type = forms.ChoiceField(
#         choices=[('user', 'User'), ('vendor', 'Vendor')],
#         label='Register As:',
#         widget=forms.RadioSelect(attrs={'class': 'form-check-inline'})
#     )
#
#     class Meta:
#         model = User
#         fields = ['user_type', 'username', 'name', 'email', 'country_code', 'phone_number', 'profile_picture', 'password1', 'password2']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
#             'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         user_type = kwargs.pop('user_type', 'user')
#         super().__init__(*args, **kwargs)
#
#         if user_type == 'vendor':
#             self.fields['profile_picture'].label = 'Logo'
#             self.fields['profile_picture'].widget = forms.ClearableFileInput(attrs={'class': 'form-control'})
#         else:
#             self.fields['profile_picture'].label = 'Profile Picture'
#
#     def clean_phone_number(self):
#         phone_number = self.cleaned_data.get('phone_number')
#         country_code = self.cleaned_data.get('country_code')
#         if phone_number and country_code:
#             return f'{country_code} {phone_number}'
#         return phone_number


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    country_code = CountryField().formfield(
        widget=CountrySelectWidget(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'type': 'tel'
        })
    )

    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=[('user', 'User'), ('vendor', 'Vendor')],
        label='Register As:',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['user_type', 'username', 'name', 'email', 'country_code', 'phone_number', 'profile_picture', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', 'user')
        super().__init__(*args, **kwargs)

        if user_type == 'vendor':
            self.fields['profile_picture'].label = 'Logo'
            self.fields['profile_picture'].widget = forms.ClearableFileInput(attrs={'class': 'form-control'})
        else:
            self.fields['profile_picture'].label = 'Profile Picture'

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        country_code = self.cleaned_data.get('country_code')
        if phone_number and country_code:
            return f'{country_code} {phone_number}'
        return phone_number


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
        fields = ['item_name', 'item_description', 'item_price', 'item_image_url', 'item_image']
        widgets = {
            'item_image': forms.ClearableFileInput(attrs={'multiple': False}),  # Widget to handle file uploads
        }


class StoreItemSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False)


class CustomItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['item_name', 'item_description', 'item_price', 'item_image_url', 'item_image']
        widgets = {
            'item_image': forms.ClearableFileInput(attrs={'multiple': False}),  # Widget to handle file uploads
        }


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
