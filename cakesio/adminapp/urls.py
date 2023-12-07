from django.urls import path
from . import views

urlpatterns = [
    path('admin_login',views.admin_login,name="adminlogin"),
    path('admin_dashboard',views.admin_dashboard,name="admin_dashboard"),
    path('admin_user',views.admin_user,name="admin_user"),
    path('block_user<int:user_id>',views.block_user,name='block_user'),
    path('unblock_user<int:user_id>',views.unblock_user,name='unblock_user'),
    path('admin_orders',views.admin_orders,name="admin_orders"),
    path('admin_category',views.admin_category,name="admin_category"),
    path('admin_editcategory/<int:id>/',views.admin_editcategory,name="admin_editcategory"),
    path('admin_product',views.admin_product,name="admin_product"),
    path('admin_addproduct',views.admin_addproduct,name="admin_addproduct"),
    path('admin_editproduct/<int:id>/',views.admin_editproduct,name="admin_editproduct"),
    path('product_delete/<int:id>',views.product_delete,name='product_delete'),
    path('category_delete/<int:id>',views.category_delete,name="category_delete"),
    path('admin_logout',views.admin_logout,name="admin_logout"),
    path('order_details/<int:order_id>/',views.order_details,name="order_details"),
    path('banners',views.banner,name="banners"),
    path('admin_editbanner/<int:id>/',views.admin_editbanner,name="admin_editbanner"),
    path('sales_report',views.sales_report,name="sales_report"),
    path('product_variation',views.product_variation,name="product_variation"),
    path('coupon',views.coupon,name="coupon"),
   

]