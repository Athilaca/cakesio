from django import forms
from .models import Product




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price', 'description', 'images', 'stock', 'oldprice', 'front_image', 'top_image']
    
    