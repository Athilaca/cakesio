from django.db import models
from django.utils import timezone
# from .views import calculate_discounted_price

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    description=models.CharField(max_length=300,blank=True)
    category_image=models.ImageField(upload_to='photos/category',blank=True)

    def __str__(self):
        return self.category_name
    
class SeasonalOffer(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.IntegerField()
   
    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date

    def __str__(self):
        return self.name    


class Product(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    oldprice=models.IntegerField(default=0)
    price=models.IntegerField()
    description=models.TextField(max_length=500,blank=True)
    images=models.ImageField(upload_to='photos/products')
    
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    created_date=models.DateField(default=timezone.now)
    front_image=models.ImageField(upload_to='photos/products',blank=True)
    top_image=models.ImageField(upload_to='photos/products',blank=True)
    is_deleted=models.BooleanField(default=False)
    is_seasonal = models.BooleanField(default=False)
    seasonal_offer = models.ForeignKey(SeasonalOffer, on_delete=models.SET_NULL, null=True, blank=True, related_name='discounted_products')

    
 
    def get_price(self):
        if self.is_seasonal and self.seasonal_offer:
            # Calculate and return the seasonal price and discount amount
            original_price = self.price
            discount_percentage = self.seasonal_offer.discount_percentage

            # Calculate discounted price
            discount_amount = (original_price * discount_percentage) / 100
            seasonal_price = original_price - discount_amount

            return seasonal_price
        else:
            # Return the regular price
            return self.price


    def soft_delete(self):
        self.is_deleted = True
        self.save()
    
    def __str__(self):
        return self.product_name

class Banner(models.Model):
    banner1=models.ImageField(upload_to='photos/banners',blank=True)
    banner2=models.ImageField(upload_to='photos/banners',blank=True)
    banner3=models.ImageField(upload_to='photos/banners',blank=True)
    offer_banner1=models.ImageField(upload_to='photos/banners',blank=True)
    offer_banner2=models.ImageField(upload_to='photos/banners',blank=True)
    offer_banner3=models.ImageField(upload_to='photos/banners',blank=True)
    
