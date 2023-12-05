from django.db import models
from cakeapp.models import CustomUser,ShippingAddress
from adminapp.models import Product
from django.utils import timezone

from django.urls import reverse

# # Create your models here.




class  Variation(models.Model):
    weight=models.DecimalField(max_digits=5,decimal_places=1)
    price=models.IntegerField()
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    is_delete=models.BooleanField(default=False)
    created_date=models.DateTimeField( auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    offer_price=models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        return str( self.product)
    # def soft_delete(self):
    #     self.is_delete=True
    #     self.is_available=False
    #     self.save()

    

    # def get_id(self):
    #     return reverse("edit-variant",args=[self.product.id,self.id])



class CartItem(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    variations=models.ForeignKey(Variation,on_delete=models.CASCADE,null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status=models.BooleanField(default=False)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  
    def save(self, *args, **kwargs):
        # Calculate the subtotal
        # if self.variations.product:
        #     self.subtotal = self.quantity * self.variations.price
        # else:
        #     self.subtotal = 0.00
        if self.discounted_price:
            self.subtotal=self.quantity* self.discounted_price
        elif self.variations.product:
            self.subtotal= self.quantity * self.variations.price
        else:
            self.subtotal = 0.00       
        
        super(CartItem, self).save(*args, **kwargs)
       
class OrderItems(models.Model):
    variant=models.ForeignKey(Variation,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discounted_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=40, default="Pending")
    is_paid = models.BooleanField(default=False)
    
class Order(models.Model):
    new_order = models.ManyToManyField(OrderItems)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_date=models.DateTimeField( default=timezone.now)
    full_name=models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=50)
    district=models.CharField(max_length=50)
    pincode=models.CharField(max_length=6)
    unlisted = models.BooleanField(default=False)
    payment_method=models.CharField(max_length=50)
    order_notes=models.CharField(max_length=50)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=40, default="Pending")
    
    def get_day(self):
        return self.created_date.day
    
    def get_week(self):
        return self.created_date.isocalendar()[1]

    def get_month(self):
        return self.created_date.month

    def get_year(self):
        return self.created_date.year


class Coupon(models.Model):
    users = models.ManyToManyField(CustomUser, blank=True)
    code = models.CharField(max_length=50)
    discount_percentage = models.PositiveIntegerField()
    expiry_date = models.DateField()
   

    def __str__(self):
        return self.code

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.first_name}'s Wallet"

