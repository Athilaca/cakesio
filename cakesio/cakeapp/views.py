from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from cakeapp.models import *
from storeapp.models import *
from adminapp.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from random import randint
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from . forms import ImageForm
from django.db.models import Q
from .models import *





# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request,category_slug=None,price_range=None):
   
        banner=Banner.objects.all()
        newly_added_products = Product.objects.filter(is_deleted=False).order_by('-id')[:10]
        categories=Category.objects.all()
        products = Product.objects.filter(is_deleted=False)
        
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category=category,is_deleted=False)
        else:
            products = Product.objects.filter(is_deleted=False)

        if price_range:
            
          
            if price_range == '0-300':
                products = products.filter(price__gte=0, price__lte=300)
            elif price_range == '400-600':
                products = products.filter(price__gt=400, price__lte=600)
            elif price_range == '600-800':
                products = products.filter(price__gt=600, price__lte=800)
            elif price_range == '800-1000':
                products = products.filter(price__gt=800, price__lte=1000)
            elif price_range == '1000+':
                products = products.filter(price__gt=1000)

        
        search_query = request.GET.get('search')
        if search_query:
            products = products.filter(
            Q(product_name__icontains=search_query) |  # Adjust 'name' to the field you want to search
            Q(description__icontains=search_query)  # Add more fields if needed
            ) 
        
           
    
        return render(request,'home.html',{'datas':products,'categories':categories,'banners':banner,'newly_added_products': newly_added_products})
  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perform_login(request):
   
    if request.user.is_authenticated :
        return redirect('index')
    
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')
          
     

        
        myuser = authenticate(username=email,password=password)

        if myuser is not None and myuser.is_active:
            login(request,myuser)
            return redirect('index')
        else:
            messages.error(request,'invalid email or password')
            
    return render(request,'login.html')

def signup(request):
    if request.user.is_authenticated :
        return redirect('home')
    
    referral_code = None
    new_user = None
    if request.method=='POST':
        if 'otp' not in request.POST:  
            first_name=request.POST.get("first_name")
            last_name=request.POST.get("last_name")
            email=request.POST.get("email")
            password=request.POST.get("password")
            confirmpassword=request.POST.get("confirmpassword")
            phone_number=request.POST.get("phone_number")
            referral_code = request.POST.get('referral_code')
           
            if password!=confirmpassword :
                messages.warning(request,'password is incorrect')
                return redirect('/signup')
            
            try:
                if CustomUser.objects.get(first_name=first_name,last_name=last_name):
                    messages.info(request,'username is taken')
                    return redirect('/signup')
                    
            except CustomUser.DoesNotExist:
                pass    
        

            try:
                if CustomUser.objects.get(email=email):
                    messages.info(request,'email is taken')
                    return redirect('/signup')
            except CustomUser.DoesNotExist:
                pass 
            
            request.session["first_name"]=first_name
            request.session["last_name"]=last_name
            request.session["password"]=password
            request.session["email"]=email
            request.session["phone_number"]=phone_number  
            request.session["referral_code"]=referral_code
 

            otp = randint(1000, 9999)
            send_mail(
                    'Your OTP for login at cakesio',
                    f'Your OTP is: {otp}',
                    'athilaca26@gmail.com',  # Sender's email
                    [email],  # Recipient's email (user's email)
                    fail_silently=False,
                )  
            request.session["otp"]=otp
            print(otp)
            messages.success(request,'please enter the otp to login!')  
            
        else:    
            new_otp=str(request.POST.get("otp")).strip()
            stored_otp =str( request.session.get('otp')).strip()
            print(new_otp)
            print(stored_otp)
            if stored_otp == new_otp:
                new_user=CustomUser.objects.create_user(first_name=request.session.get('first_name'),last_name=request.session.get('last_name'),
                email=request.session.get('email'),phone_number=request.session.get('phone_number'))
                new_user.set_password(request.session['password'])
                new_user.save()
                
            else:
                messages.error(request,'invalid otp')

            referral_code=request.session.get('referral_code')
            if referral_code and new_user:
                print(referral_code)
                try:
                    
                    referrer = CustomUser.objects.get(referral_code=referral_code)
                    referral=Referral.objects.create(referrer=referrer, referred_user=new_user)

                      
                    referrer_wallet, _ = Wallet.objects.get_or_create(user=referrer)
                    referrer_wallet.balance += 100
                    referrer_wallet.save()

                   
                    referred_user_wallet, _ = Wallet.objects.get_or_create(user=new_user)
                    referred_user_wallet.balance += 50
                    referred_user_wallet.save()
                
                except CustomUser.DoesNotExist:
                    pass 

            return redirect('index') 
    return render(request,'signup.html')




@login_required
def perform_logout(request):
    logout(request)
    return redirect(perform_login)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    banner=Banner.objects.all()
    category=Category.objects.all()
    product=Product.objects.filter(is_deleted=False)[:10]
    return render(request,'index.html',{'banner':banner,'category':category,'product':product})


def product_detail(request,product_id):

    data=Product.objects.get(id=product_id)
    
  
    return render(request,'product-details.html',{'data':data})


def account(request):
   
    if  not request.user.is_authenticated:
        return redirect('login')
    addresses=ShippingAddress.objects.filter(user=request.user)
    order=Order.objects.filter(user=request.user).order_by('-id')
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'balance': 0.00})
    referral_code = request.user.referral_code if request.user.referral_code else "N/A"
    referral_link = request.build_absolute_uri(f'/signup?ref={referral_code}')


    if request.method=="POST":
        full_name=request.POST.get("full_name")
        address=request.POST.get("address")
        city=request.POST.get("city")
        district=request.POST.get("district")
        pincode=request.POST.get("pincode")
        phone_number=request.POST.get("phone_number")
        
        valid=True

        if not full_name.isalpha():
            messages.error(request,"Full name should contain only alphabetic characters")
            valid = False

        if not city.isalpha():
            messages.error(request,"City should contain only alphabetic characters")
            valid = False

        if not pincode.isdigit() or len(pincode) != 6:
             messages.error(request,"Pincode should be a 6-digit number")
             valid = False

        if not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(request,"Phone number should be a 10-digit number")
            valid = False

        if address.isdigit() :
            messages.error(request,"Address should contain text ")
            valid = False
        
        if valid:
           myuser=ShippingAddress(full_name=full_name,address=address,city=city,district=district,pincode=pincode,phone_number=phone_number)
           myuser.save()     
           return redirect(account)
    return render (request,"account.html",{'address':addresses,'orders':order,'wallet':wallet,'referral_link': referral_link,'referral_code':referral_code})


def profile(request):
    return render (request,"profile.html")

def change_password(request):
    if request.method == 'POST':
        fname=request.POST['fname']
        email=request.POST['email']
        current_password = request.POST['password']
        new_password = request.POST['npassword']
        
        user = request.user

        user.email = email
        user.first_name = fname
        
        if current_password and new_password:
           if user.check_password(current_password):
           
                user.set_password(new_password)
                # Update the user's session to avoid automatic logout
                update_session_auth_hash(request, user)

        user.save()
        messages.success(request,'profile updated succesfully')     
           
            
           
        
        return redirect(account)
           
    
    return render(request, 'account.html')

def delete_address(request,address_id):
    cart=ShippingAddress.objects.get(id=address_id)
    cart.delete()
   
    return redirect(account)




def update_price(request):
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        selected_weight = request.GET.get('selected_weight')
        product=Product.objects.get(id=product_id)
        variations=Variation.objects.get(product=product,weight=selected_weight)
        new_price = variations.get_price()
        new_stock= variations.stock
       
        return JsonResponse({'new_price': new_price, 'new_stock': new_stock})

def order_view(request,order_id):
    order_details=Order.objects.get(id=order_id)
    order_items=Order.objects.get(id=order_id).new_order.all().select_related('variant')
    
    context={'order_items':order_items,'order_details':order_details}

    return render (request,'order-view.html',context)


def order_cancel(request,order_id):
    order=Order.objects.get(id=order_id)
    payment_method = order.payment_method
    order.delete()

    if payment_method != "Cash_on_delivery":
       
        user = order.user
        wallet = Wallet.objects.get(user=user)
        wallet.balance += order.bill_amount
        wallet.save()

        
    return redirect(account)



@login_required
def update_profile_pic(request):
   form=ImageForm(request.POST or None, request.FILES or None, instance=request.user)
   if form.is_valid():
        form.save()
        return JsonResponse({'message': 'works'})
   context={'form':form}
   return render(request,'profile.html',context)

