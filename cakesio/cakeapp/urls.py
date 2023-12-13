from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("login",views.perform_login,name='login'),
    path("signup",views.signup,name='signup'),
    path("logout",views.perform_logout,name="logout"),
    path("home",views.home,name='home'),
    path("product_detail/<int:product_id>/",views.product_detail,name="product_detail"),
    path("delete_address<int:address_id>",views.delete_address,name="delete_address"),
    path("account",views.account,name="account"),
    path("change_password",views.change_password,name="change_password"),
    path("profile",views.profile,name="profile"),
    path("update_price",views.update_price,name="update_price"),
    path("order_view/<int:order_id>/",views.order_view,name="order_view"),
    path("order_cancel/<int:order_id>/",views.order_cancel,name="order_cancel"),
    path("update_profile_pic",views.update_profile_pic,name="update_profile_pic"),
    path('products/category/<slug:category_slug>/',views. home, name='home'),
    path('home/<str:price_range>/',views.home, name='home_price_range'),
    path('about',views.about,name="about")
]
