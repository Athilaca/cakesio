from django.urls import path
from . import views

urlpatterns = [
    path('cart',views.shop_cart,name="cart"),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path("delete_cart/<int:cart_id>/",views.delete_cart,name="delete_cart"),
    path("order",views.order,name="order"),
    path("new_address",views.new_address,name="new_address"),
    path("apply_coupon",views.apply_coupon,name="apply_coupon"),
    path('update_quantity/',views.update_quantity, name='update_quantity'), 
    path('create_order',views.create_order,name="create_order"),
    path('success',views.success,name="success"),
  
]