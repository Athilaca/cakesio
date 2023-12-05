from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Variation)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(OrderItems)
admin.site.register(Coupon)
admin.site.register(Wallet)