from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Order
from .forms import OrderForm  # Define this form for handling orders
from django.http import HttpResponse


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
