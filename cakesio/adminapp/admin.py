from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Banner)
admin.site.register(SeasonalOffer)

# class ProductAdmin(admin.ModelAdmin):
#     list_display=('product_name','description','price')
#     prepopulated_fields={'slug':('product_name',)}
# admin.site.register(Product,ProductAdmin)