# store/forms.py

from django import forms
from .models import Product, Order, OrderItem, ShippingDetails, Vendor
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class VendorRegistrationForm(forms.ModelForm):
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
    logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Vendor
        fields = ['name', 'description', 'email', 'country_code', 'phone_number', 'location', 'logo', 'password']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Vendor.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        country_dict = {'AF': '93', 'AX': '358-18', 'AL': '355', 'DZ': '213', 'AS': '1-684', 'AD': '376', 'AO': '244', 'AI': '1-264', 'AQ': '672', 'AG': '1-268', 'AR': '54', 'AM': '374', 'AW': '297', 'AU': '61', 'AT': '43', 'AZ': '994', 'BH': '973', 'BD': '880', 'BB': '1-246', 'BY': '375', 'BE': '32', 'BZ': '501', 'BJ': '229', 'BM': '1-441', 'BT': '975', 'BO': '591', 'BQ': '599', 'BA': '387', 'BW': '267', 'BV': '0055', 'BR': '55', 'IO': '246', 'BN': '673', 'BG': '359', 'BF': '226', 'BI': '257', 'KH': '855', 'CM': '237', 'CA': '1', 'CV': '238', 'KY': '1-345', 'CF': '236', 'TD': '235', 'CL': '56', 'CN': '86', 'CX': '61', 'CC': '61', 'CO': '57', 'KM': '269', 'CG': '242', 'CK': '682', 'CR': '506', 'CI': '225', 'HR': '385', 'CU': '53', 'CW': '599', 'CY': '357', 'CZ': '420', 'CD': '243', 'DK': '45', 'DJ': '253', 'DM': '1-767', 'DO': '1-809 and 1-829', 'EC': '593', 'EG': '20', 'SV': '503', 'GQ': '240', 'ER': '291', 'EE': '372', 'SZ': '268', 'ET': '251', 'FK': '500', 'FO': '298', 'FJ': '679', 'FI': '358', 'FR': '33', 'GF': '594', 'PF': '689', 'TF': '262', 'GA': '241', 'GM': '220', 'GE': '995', 'DE': '49', 'GH': '233', 'GI': '350', 'GR': '30', 'GL': '299', 'GD': '1-473', 'GP': '590', 'GU': '1-671', 'GT': '502', 'GG': '44-1481', 'GN': '224', 'GW': '245', 'GY': '592', 'HT': '509', 'HM': '672', 'HN': '504', 'HK': '852', 'HU': '36', 'IS': '354', 'IN': '91', 'ID': '62', 'IR': '98', 'IQ': '964', 'IE': '353', 'IL': '972', 'IT': '39', 'JM': '1-876', 'JP': '81', 'JE': '44-1534', 'JO': '962', 'KZ': '7', 'KE': '254', 'KI': '686', 'XK': '383', 'KW': '965', 'KG': '996', 'LA': '856', 'LV': '371', 'LB': '961', 'LS': '266', 'LR': '231', 'LY': '218', 'LI': '423', 'LT': '370', 'LU': '352', 'MO': '853', 'MG': '261', 'MW': '265', 'MY': '60', 'MV': '960', 'ML': '223', 'MT': '356', 'IM': '44-1624', 'MH': '692', 'MQ': '596', 'MR': '222', 'MU': '230', 'YT': '262', 'MX': '52', 'FM': '691', 'MD': '373', 'MC': '377', 'MN': '976', 'ME': '382', 'MS': '1-664', 'MA': '212', 'MZ': '258', 'MM': '95', 'NA': '264', 'NR': '674', 'NP': '977', 'NL': '31', 'NC': '687', 'NZ': '64', 'NI': '505', 'NE': '227', 'NG': '234', 'NU': '683', 'NF': '672', 'KP': '850', 'MK': '389', 'MP': '1-670', 'NO': '47', 'OM': '968', 'PK': '92', 'PW': '680', 'PS': '970', 'PA': '507', 'PG': '675', 'PY': '595', 'PE': '51', 'PH': '63', 'PN': '870', 'PL': '48', 'PT': '351', 'PR': '1-787 and 1-939', 'QA': '974', 'RE': '262', 'RO': '40', 'RU': '7', 'RW': '250', 'SH': '290', 'KN': '1-869', 'LC': '1-758', 'PM': '508', 'VC': '1-784', 'BL': '590', 'MF': '590', 'WS': '685', 'SM': '378', 'ST': '239', 'SA': '966', 'SN': '221', 'RS': '381', 'SC': '248', 'SL': '232', 'SG': '65', 'SX': '1721', 'SK': '421', 'SI': '386', 'SB': '677', 'SO': '252', 'ZA': '27', 'GS': '500', 'KR': '82', 'SS': '211', 'ES': '34', 'LK': '94', 'SD': '249', 'SR': '597', 'SJ': '47', 'SE': '46', 'CH': '41', 'SY': '963', 'TW': '886', 'TJ': '992', 'TZ': '255', 'TH': '66', 'BS': '1-242', 'TL': '670', 'TG': '228', 'TK': '690', 'TO': '676', 'TT': '1-868', 'TN': '216', 'TR': '90', 'TM': '993', 'TC': '1-649', 'TV': '688', 'UG': '256', 'UA': '380', 'AE': '971', 'GB': '44', 'US': '1', 'UM': '1', 'UY': '598', 'UZ': '998', 'VU': '678', 'VA': '379', 'VE': '58', 'VN': '84', 'VG': '1-284', 'VI': '1-340', 'WF': '681', 'EH': '212', 'YE': '967', 'ZM': '260', 'ZW': '263'}
        country = self.cleaned_data.get('country_code')
        country_code = country_dict[country]
        if phone_number and country_code:
            corrected_phone_number = phone_number.lstrip('0')
            full_phone_number = f'{country_code}{corrected_phone_number}'
        else:
            full_phone_number = phone_number
        if Vendor.objects.filter(phone_number=full_phone_number).exists():
            raise forms.ValidationError('This phone number is already in use.')
        return full_phone_number


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
