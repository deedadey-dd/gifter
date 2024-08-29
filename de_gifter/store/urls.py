from django.urls import path
from . import views

# app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy_item/<int:product_id>/', views.buy_item, name='buy_item'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('add-product/', views.add_product, name='add_product'),
    path('my-products/', views.my_products, name='my_products'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('vendor-profile/', views.vendor_profile, name='vendor_profile'),
    path('edit-vendor-profile/', views.edit_vendor_profile, name='edit_vendor_profile'),
    path('register/vendor/', views.vendor_register, name='vendor_register'),
    path('confirm_vendor_phone/<uidb64>/', views.confirm_vendor_phone, name='confirm_vendor_phone'),
    path('activate_vendor/<uidb64>/<token>/', views.activate_vendor, name='activate_vendor'),
]
