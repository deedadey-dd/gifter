# main/views.py
import requests
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import (UserRegistrationForm, UserLoginForm, ItemForm, ItemImageForm, WishlistItemForm,
                    VendorRegistrationForm, PhoneConfirmationForm, WishlistForm, StoreItemSearchForm, CustomItemForm,
                    ProfileForm, ContributionForm)
from .models import User, Vendor, Category, Item, ItemImage, Wishlist, WishlistItem, Contribution
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .tokens import account_activation_token
import random
import os
from django.utils import timezone


sms_endpoint = os.environ['SMS_ENDPOINT']
sms_apikey = os.environ['SMS_API']

# Define the list of colors
all_colors = [
    '009FBD', '3FA2F6', 'FF4191', '36BA98', '597445', 'E0A75E',
    'FF6969', '06D001', '83B4FF', 'C738BD', 'A1DD70', 'D2649A',
    '40A578', 'FF76CE', 'AF8260', '41B06E', '5755FE'
]


def home(request):
    items = Item.objects.all().order_by('-added_to_wishlist_count')
    wishlists = Wishlist.objects.filter(user=request.user) if request.user.is_authenticated else []

    all_colors = ['009FBD', '3FA2F6', 'FF4191', '36BA98', '597445', 'E0A75E', 'FF6969', '06D001',
                  '83B4FF', 'C738BD', 'A1DD70', 'D2649A', '40A578', 'FF76CE', 'AF8260', '41B06E', '5755FE']

    items_with_colors = [(item, random.choice(all_colors)) for item in items]

    context = {
        'items_with_colors': items_with_colors,
        'wishlists': wishlists
    }
    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email is confirmed
            phone_pin = user.generate_confirmation_pin()
            print(phone_pin)
            user.save()
            send_confirmation_email(request, user)
            messages.success(request, 'Please confirm your email and phone number to complete registration.')
            # send user pin to the user's phone number using mnotify account 0265550354
            send_confirmation_pin(user)

            return redirect('confirm_phone', uidb64=urlsafe_base64_encode(force_bytes(user.pk)))

    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def send_confirmation_pin(user):
    data = {
        'recipient[]': [f'{user.phone_number}'],
        'sender': 'Dee Code',
        'message': f'Enter the following PIN to confirm your phone number\n {user.phone_confirmation_pin} third msg',
    }
    url = sms_endpoint + '?key=' + sms_apikey
    requests.post(url, data)
    print(f'sent {user.phone_confirmation_pin} to {user.phone_number}')


def send_confirmation_email(request, user):
    mail_subject = 'Activate your account.'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': request.META.get('HTTP_HOST', 'localhost'),  # Default to localhost if HTTP_HOST is not available
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })

    try:
        send_mail(
            mail_subject,
            message,
            from_email=os.getenv('EMAIL_USER', 'EMAIL_USER'),  # Default to a fallback email
            recipient_list=[user.email],
            fail_silently=False  # Set to False to raise exceptions if sending fails
        )
        print(f'Confirmation email sent to {user.email}')  # Log for debugging
    except Exception as e:
        print(f'Error sending confirmation email: {e}')  # Log the exception for debugging


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        if user.phone_confirmed:
            user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')


def confirm_phone(request, uidb64):
    user = get_object_or_404(User, pk=force_str(urlsafe_base64_decode(uidb64)))
    if request.method == 'POST':
        form = PhoneConfirmationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['pin'] == user.phone_confirmation_pin:
                user.phone_confirmed = True
                if user.email_confirmed:
                    user.is_active = True
                user.save()
                messages.success(request, 'Your phone number has been confirmed.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid PIN. Please try again.')
    else:
        form = PhoneConfirmationForm()
    return render(request, 'confirm_phone.html', {'form': form, 'uid': uidb64})


# @login_required
def resend_pin(request):
    user = request.user
    phone_pin = user.generate_confirmation_pin()
    # Logic to send SMS to user's phone using mnotify 026 account
    data = {
        'recipient[]': [f'{user.phone_number}'],
        'sender': 'Dee Code',
        'message': f'Enter the following PIN to confirm your phone number\n {phone_pin} third msg',
    }
    url = sms_endpoint + '?key=' + sms_apikey
    response = requests.post(url, data)
    messages.success(request, 'A new PIN has been sent to your phone number.')
    return redirect('confirm_phone', uidb64=urlsafe_base64_encode(force_bytes(user.pk)))


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=identifier, password=password) or authenticate(request, email=identifier, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username/email or password')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            for file in request.FILES.getlist('image_url'):
                ItemImage.objects.create(item=item, image_url=file)
            return redirect('item_list')
    else:
        form = ItemForm()
        image_form = ItemImageForm()
    return render(request, 'add_item.html', {'form': form, 'image_form': image_form})


def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})


# def add_vendor(request):
#     if request.method == 'POST':
#         form = VendorRegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('vendor_list')
#     else:
#         form = VendorRegistrationForm()
#     return render(request, 'add_vendor.html', {'form': form})


def register_vendor(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.generate_confirmation_pin()
            vendor.save()
            send_confirmation_email(request, vendor)
            messages.success(request, 'Please confirm your email and phone number to complete registration.')
            return redirect('login')
    else:
        form = VendorRegistrationForm()
    return render(request, 'register_vendor.html', {'form': form})


def send_vendor_confirmation_email(request, vendor):
    mail_subject = 'Activate your account.'
    message = render_to_string('vendor_acc_active_email.html', {
        'vendor': vendor,
        'domain': request.META['HTTP_HOST'],
        'uid': urlsafe_base64_encode(force_bytes(vendor.pk)),
        'token': account_activation_token.make_token(vendor),
    })
    send_mail(mail_subject, message, from_email=os.environ['EMAIL_USER'], recipient_list=[vendor.email])


def activate_vendor(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        vendor = Vendor.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Vendor.DoesNotExist):
        vendor = None
    if vendor is not None and account_activation_token.check_token(vendor, token):
        vendor.email_confirmed = True
        if vendor.phone_confirmed:
            vendor.verification = 'verified'
        vendor.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register_vendor')


def confirm_vendor_phone(request, uidb64):
    vendor = get_object_or_404(Vendor, pk=force_str(urlsafe_base64_decode(uidb64)))
    if request.method == 'POST':
        form = PhoneConfirmationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['pin'] == vendor.phone_confirmation_pin:
                vendor.phone_confirmed = True
                if vendor.email_confirmed:
                    vendor.verification = 'verified'
                vendor.save()
                messages.success(request, 'Your phone number has been confirmed.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid PIN. Please try again.')
    else:
        form = PhoneConfirmationForm()
    return render(request, 'confirm_vendor_phone.html', {'form': form, 'uid': uidb64})


@login_required
def resend_vendor_pin(request):
    vendor = request.user.vendor
    vendor.generate_confirmation_pin()
    # Implement logic to send the pin to the vendor's phone number
    messages.success(request, 'A new PIN has been sent to your phone number.')
    return redirect('confirm_vendor_phone', uidb64=urlsafe_base64_encode(force_bytes(vendor.pk)))


def update_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_list')
    else:
        form = VendorRegistrationForm(instance=vendor)
    return render(request, 'update_vendor.html', {'form': form})


def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'vendors': vendors})


@login_required
def create_wishlist(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            messages.success(request, 'Wishlist created successfully.')
            return redirect('wishlists')
    else:
        form = WishlistForm()
    return render(request, 'create_wishlist.html', {'form': form})


@login_required
def edit_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if request.method == 'POST':
        form = WishlistForm(request.POST, instance=wishlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Wishlist updated successfully.')
            return redirect('wishlists')
    else:
        form = WishlistForm(instance=wishlist)
    return render(request, 'edit_wishlist.html', {'form': form, 'wishlist': wishlist})


@login_required
def view_wishlists(request):
    wishlists = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlists.html', {'wishlists': wishlists})


@login_required
def add_store_item_to_wishlist(request, wishlist_id, item_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item = get_object_or_404(Item, id=item_id)
    wishlist_item = WishlistItem(
        wishlist=wishlist,
        item=item,
        item_name=item.name,
        item_description=item.description,
        item_price=item.price,
        item_image_url=item.image_url,
    )
    wishlist_item.save()
    messages.success(request, 'Item added to wishlist.')
    return redirect('view_wishlist', wishlist_id=wishlist_id)


@login_required
def add_custom_item_to_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if request.method == 'POST':
        form = WishlistItemForm(request.POST)
        if form.is_valid():
            wishlist_item = form.save(commit=False)
            wishlist_item.wishlist = wishlist
            wishlist_item.save()
            messages.success(request, 'Custom item added to wishlist.')
            return redirect('view_wishlist', wishlist_id=wishlist_id)
    else:
        form = WishlistItemForm()
    return render(request, 'add_custom_item.html', {'form': form, 'wishlist': wishlist})


# @login_required   #login is not required to view a wishlist
def view_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    items = wishlist.items.all()
    for item in items:
        item.remaining_amount = item.item_price - item.amount_paid

        # Calculate total contributed by each individual
        contributions = item.contributions.all()
        item.contributors = []
        total_contributions_by_user = contributions.values('name').annotate(
            total_contributed=Coalesce(Sum('amount'), 0.0)
        )

        for contribution in total_contributions_by_user:
            item.contributors.append({
                'name': contribution['name'],
                'total_contributed': contribution['total_contributed']
            })

        # Calculate any amount from contributions sent to extra cash
        total_contributed = sum(c['total_contributed'] for c in item.contributors)
        excess_amount = max(total_contributed - item.item_price, 0)
        item.excess_contribution = excess_amount

    today = timezone.now().date()
    wishlist.days_left = (wishlist.expiry_date - today).days

    context = {
        'wishlist': wishlist,
        'items': items,
        'user': request.user  # Pass the current user to the template
    }
    print(wishlist.days_left)
    return render(request, 'view_wishlist.html', context)


@login_required
def add_item_to_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    search_form = StoreItemSearchForm(request.GET or None)
    custom_item_form = CustomItemForm(request.POST or None, request.FILES or None)

    items = Item.objects.all()
    if 'search' in request.GET and search_form.is_valid():
        search_query = search_form.cleaned_data['search']
        items = items.filter(name__icontains(search_query))

    if 'item_id' in request.POST:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)
        wishlist_item = WishlistItem(
            wishlist=wishlist,
            item=item,
            item_name=item.name,
            item_description=item.description,
            item_price=item.price,
            item_image_url=item.image_url,
        )
        wishlist_item.save()
        messages.success(request, 'Store item added to wishlist.')
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    if custom_item_form.is_valid():
        custom_item = custom_item_form.save(commit=False)
        custom_item.wishlist = wishlist
        custom_item.save()
        messages.success(request, 'Custom item added to wishlist.')
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    return render(request, 'add_item_to_wishlist.html', {
        'wishlist': wishlist,
        'search_form': search_form,
        'custom_item_form': custom_item_form,
        'items': items,
    })


class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'password_reset_request.html'
    success_url = reverse_lazy('password_reset_done')


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')  # Redirect to the profile page or another page
    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile.html', {'form': form})


def all_wishlists(request):
    # Get the current date
    today = timezone.now().date()

    # Filter and sort wishlists
    wishlists = Wishlist.objects.filter(expiry_date__gte=today).order_by('expiry_date')

    # Calculate the number of days left, total cost, and assign a random color
    for wishlist in wishlists:
        wishlist.days_left = (wishlist.expiry_date - today).days
        wishlist.expiry_date_formatted = wishlist.expiry_date.strftime('%Y-%m-%d')

        # Assign a random color from the list
        wishlist.color = random.choice(all_colors)

        # Calculate total cost of the items in the wishlist
        # Assuming `Item` is related to `Wishlist` and has a `cost` field
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        wishlist.total_cost = sum(item.item_price for item in wishlist_items)
        wishlist.item_count = wishlist_items.count()

    # Calculate total cost and get first 3 items
    total_cost = sum(wishlist.total_cost for wishlist in wishlists)
    first_three_items = wishlists[:3]
    number_left = max(0, len(wishlists) - 3)

    context = {
        'wishlists': wishlists,
        'total_cost': total_cost,
        'first_three_items': first_three_items,
        'number_left': number_left,
    }

    return render(request, 'all_wishlists.html', context)


def update_expiry_date(request, wishlist_id):
    if request.method == 'POST':
        wishlist = get_object_or_404(Wishlist, id=wishlist_id)
        new_expiry_date = request.POST.get('expiry_date')
        if new_expiry_date:
            wishlist.expiry_date = new_expiry_date
            wishlist.save()
        return redirect('view_wishlist', wishlist_id=wishlist_id)
    return redirect('view_wishlist', wishlist_id=wishlist_id)


def remove_item_from_wishlist(request, item_id):
    # Get the WishlistItem object based on the provided item_id
    item = get_object_or_404(WishlistItem, id=item_id)

    # Ensure that the item belongs to the current user's wishlist
    if request.user == item.wishlist.user:
        # Remove the item from the wishlist
        item.delete()

        # Provide a success message
        messages.success(request, 'Item successfully removed from the wishlist.')
    else:
        # Provide an error message if the user is not authorized
        messages.error(request, 'You are not authorized to remove this item.')

    # Redirect back to the wishlist view
    return redirect('view_wishlist', wishlist_id=item.wishlist.id)


def edit_custom_item(request, item_id):
    # Get the WishlistItem object based on the provided item_id
    item = get_object_or_404(WishlistItem, id=item_id)

    # Check if the current user is the owner of the wishlist
    if request.user != item.wishlist.user:
        messages.error(request, 'You are not authorized to edit this item.')
        return redirect('view_wishlist', wishlist_id=item.wishlist.id)

    # Handle POST request (form submission)
    if request.method == 'POST':
        form = WishlistItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item successfully updated.')
            return redirect('view_wishlist', wishlist_id=item.wishlist.id)
    else:
        # Handle GET request (display form)
        form = WishlistItemForm(instance=item)

    # Render the form template
    return render(request, 'edit_custom_item.html', {'form': form, 'item': item})


# Towards Contributing

    # """
    # the view for pay_for_item that enables people to contribute to either the wishlist or an item on
    # the wishlist. the popup form should have a dropdown where the giver can select an item to contribute
    # to but the default goes to the next item in the wishlist which has not been 'Filled' or completely
    # paid for yet. If the giver's contribution is greater than the next item, the remaining should be used
    # to pay for the next item till all items are exhausted after which the remaining money should be added
    # to the receiver's cash_on_hand and also reported on the wishlist as additional cash.
    #
    # :param request:
    # :param wishlist_id:
    # :return:
    # """


def pay_for_item(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id)
    wishlist = item.wishlist
    next_items = wishlist.items.filter(status='Pending').order_by('id')

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            message = form.cleaned_data['message']
            contributor_name = form.cleaned_data['name']
            contributor_phone = form.cleaned_data['phone']

            # this is the remaining contribution money
            remaining_amount = amount

            for next_item in next_items:
                if remaining_amount <= 0:
                    break
                if next_item.status == 'Filled':
                    continue

                if remaining_amount >= next_item.item_price - next_item.amount_paid:
                    contribution_amount = next_item.item_price - next_item.amount_paid
                    next_item.amount_paid = next_item.item_price
                    next_item.status = 'Filled'
                else:
                    contribution_amount = remaining_amount
                    next_item.amount_paid += contribution_amount
                    next_item.status = 'Partially Filled'

                remaining_amount -= contribution_amount

                # Save contribution
                Contribution.objects.create(
                    wishlist_item=next_item,
                    name=contributor_name,
                    amount=contribution_amount,
                    message=message,
                    phone=contributor_phone,
                )

                next_item.save()

            # Add remaining amount to extra cash if not all used
            if remaining_amount > 0:
                wishlist.extra_cash += remaining_amount
                wishlist.save()

            messages.success(request, 'Your contribution has been successfully processed!')
            return redirect('view_wishlist', wishlist_id=wishlist.id)
    else:
        form = ContributionForm()

    return render(request, 'pay_for_item.html', {'form': form, 'item': item})


def transfer_extra_cash(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if request.method == 'POST':
        wishlist.transfer_extra_cash()
        messages.success(request, 'Extra cash successfully moved to your cash on hand.')
    return redirect('view_wishlist', wishlist_id=wishlist_id)


def allocate_extra_cash(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)

    # Process the allocation logic here
    for item in wishlist.items.all():
        if wishlist.extra_cash > 0:
            remaining_amount = item.item_price - item.amount_paid
            if remaining_amount > 0:
                if wishlist.extra_cash >= remaining_amount:
                    item.amount_paid = item.item_price
                    wishlist.extra_cash -= remaining_amount
                else:
                    item.amount_paid += wishlist.extra_cash
                    wishlist.extra_cash = 0
                item.save()

    wishlist.save()
    messages.success(request, 'Extra cash allocated to items successfully.')
    return redirect('view_wishlist', wishlist_id=wishlist_id)

