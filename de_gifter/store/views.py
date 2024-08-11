from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order, OrderItem, Vendor
from .forms import OrderForm  # Define this form for handling orders
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


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

    return render(request, 'create_order.html', {'order_form': order_form, 'shipping_form': shipping_form})


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
