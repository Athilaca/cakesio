from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import string
from django.utils.crypto import get_random_string
#create your models here

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Generate a referral code if not already set
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)

    def generate_referral_code(self, code_length=6):
       return get_random_string(length=code_length, allowed_chars=string.ascii_uppercase + string.digits)

class ShippingAddress(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,default=1)
    full_name=models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=50)
    district=models.CharField(max_length=50)
    pincode=models.CharField(max_length=6)
    unlisted = models.BooleanField(default=False)


    def __str__(self):
        return self.address

class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_given')
    referred_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals_received')
    timestamp = models.DateTimeField(auto_now_add=True)
