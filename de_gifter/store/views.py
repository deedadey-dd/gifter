from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order, OrderItem, Vendor
from .forms import ProductForm, OrderForm, ShippingDetailsForm, VendorProfileForm, VendorRegistrationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import VendorRegistrationForm
from .models import Vendor
from main.tokens import account_activation_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import requests
import os
from main.forms import PhoneConfirmationForm

sms_endpoint = os.environ['SMS_ENDPOINT']
sms_apikey = os.environ['SMS_API']


def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.is_active = False
            vendor.generate_confirmation_pin()  # Assuming you have this method for vendors
            vendor.save()
            send_confirmation_email(request, vendor)
            send_confirmation_pin(vendor)  # Assuming you have this method for vendors
            messages.success(request, 'Please confirm your email and phone number to complete registration.')
            return redirect('confirm_phone', uidb64=urlsafe_base64_encode(force_bytes(vendor.pk)))
    else:
        form = VendorRegistrationForm()

    return render(request, 'register_vendor.html', {'form': form})


def send_confirmation_pin(vendor):
    data = {
        'recipient[]': [f'{vendor.phone_number}'],
        'sender': 'Dee Code',
        'message': f'Enter the following PIN to confirm your phone number\n {vendor.phone_confirmation_pin} third msg',
    }
    url = sms_endpoint + '?key=' + sms_apikey
    requests.post(url, data)
    print(f'sent {vendor.phone_confirmation_pin} to {vendor.phone_number}')


def send_confirmation_email(request, vendor):
    mail_subject = 'Activate your account.'
    message = render_to_string('acc_active_email.html', {
        'vendor': vendor,
        'domain': request.META.get('HTTP_HOST', 'localhost'),
        'uid': urlsafe_base64_encode(force_bytes(vendor.pk)),
        'token': account_activation_token.make_token(vendor),
    })

    try:
        send_mail(
            mail_subject,
            message,
            from_email=os.getenv('EMAIL_USER', 'EMAIL_USER'),
            recipient_list=[vendor.email],
            fail_silently=False
        )
        print(f'Confirmation email sent to {vendor.email}')
    except Exception as e:
        print(f'Error sending confirmation email: {e}')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        vendor = Vendor.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Vendor.DoesNotExist):
        vendor = None
    if vendor is not None and account_activation_token.check_token(vendor, token):
        vendor.email_confirmed = True
        if vendor.phone_confirmed:
            vendor.is_active = True
        vendor.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')


def confirm_phone(request, uidb64):
    vendor = get_object_or_404(Vendor, pk=force_str(urlsafe_base64_decode(uidb64)))
    if request.method == 'POST':
        form = PhoneConfirmationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['pin'] == vendor.phone_confirmation_pin:
                vendor.phone_confirmed = True
                if vendor.email_confirmed:
                    vendor.is_active = True
                vendor.save()
                messages.success(request, 'Your phone number has been confirmed.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid PIN. Please try again.')
    else:
        form = PhoneConfirmationForm()
    return render(request, 'confirm_phone.html', {'form': form, 'uid': uidb64})


def resend_pin(request):
    vendor = request.user
    phone_pin = vendor.generate_confirmation_pin()
    data = {
        'recipient[]': [f'{vendor.phone_number}'],
        'sender': 'Dee Code',
        'message': f'Enter the following PIN to confirm your phone number\n {phone_pin} third msg',
    }
    url = sms_endpoint + '?key=' + sms_apikey
    response = requests.post(url, data)
    messages.success(request, 'A new PIN has been sent to your phone number.')
    return redirect('confirm_phone', uidb64=urlsafe_base64_encode(force_bytes(vendor.pk)))


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')  # Adjust this to your desired redirect URL
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    # Handle adding items to the cart
    pass


def process_transaction(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    vendor = product.vendor
    amount_paid = float(request.POST.get('amount', 0))
    fee_percentage = vendor.fee_percentage
    fee_amount = (amount_paid * fee_percentage) / 100
    vendor_earnings = amount_paid - fee_amount

    # Save or process the transaction here
    # e.g., update vendor earnings, handle payment, etc.

    return HttpResponse(f"Transaction processed. Vendor earns: {vendor_earnings}, Fee amount: {fee_amount}")


def checkout(request):
    # Handle checkout process
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process order
            pass
    else:
        form = OrderForm()
    return render(request, 'store/checkout.html', {'form': form})


def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        shipping_form = ShippingDetailsForm(request.POST)

        if order_form.is_valid() and shipping_form.is_valid():
            order = order_form.save()
            shipping_details = shipping_form.save(commit=False)
            shipping_details.order = order
            shipping_details.save()
            return redirect('order_success')
    else:
        order_form = OrderForm()
        shipping_form = ShippingDetailsForm()

    return render(request, 'store/create_order.html', {'order_form': order_form, 'shipping_form': shipping_form})


@login_required
def buy_item(request, product_id):
    # Get the product object
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle order form submission
        order_form = OrderForm(request.POST)
        shipping_form = ShippingDetailsForm(request.POST)

        if order_form.is_valid() and shipping_form.is_valid():
            # Create and save the order
            order = order_form.save(commit=False)
            order.user = request.user
            order.total_amount = product.price  # Or calculate total amount based on quantity, etc.
            order.save()

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1  # Assuming a quantity of 1 for simplicity
            )

            # Save shipping details
            shipping_details = shipping_form.save(commit=False)
            shipping_details.order = order
            shipping_details.save()

            # Redirect to order confirmation or success page
            return redirect('store:order_confirmation', order_id=order.id)
        else:
            # Handle form errors
            return render(request, 'store/buy_item.html', {
                'product': product,
                'order_form': order_form,
                'shipping_form': shipping_form
            })

    else:
        # Initialize forms
        order_form = OrderForm()
        shipping_form = ShippingDetailsForm()

    return render(request, 'store/buy_item.html', {
        'product': product,
        'order_form': order_form,
        'shipping_form': shipping_form
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'store/order_confirmation.html', {
        'order': order
    })


@login_required
def my_products(request):
    # Get the vendor profile for the currently logged-in user
    vendor = get_object_or_404(Vendor, user=request.user)

    # Fetch products belonging to the vendor
    products = vendor.products.all()

    context = {
        'products': products,
    }
    return render(request, 'store/my_products.html', context)


@login_required
def my_orders(request):
    # Fetch orders for the logged-in vendor
    vendor = getattr(request.user, 'vendor', None)  # Get the vendor instance if it exists
    if vendor:
        orders = Order.objects.filter(vendor=vendor)  # Assuming an Order model with a vendor field
    else:
        orders = []

    context = {
        'orders': orders,
    }
    return render(request, 'store/my_orders.html', context)


@login_required
def vendor_profile(request):
    # Get the vendor profile for the currently logged-in user
    vendor = get_object_or_404(Vendor, user=request.user)

    context = {
        'vendor': vendor,
    }
    return render(request, 'store/vendor_profile.html', context)


@login_required
def edit_vendor_profile(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_profile')
    else:
        form = VendorProfileForm(instance=vendor)

    context = {
        'form': form,
    }
    return render(request, 'store/edit_vendor_profile.html', context)
