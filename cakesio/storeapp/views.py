from django.shortcuts import render,redirect
from cakeapp.models import *
from adminapp.models import *
from . models import *
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
import razorpay
from decimal import Decimal
from django.db.models import Sum
from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.


  
def add_cart(request,product_id):
        
    if request.method == 'POST':
        if  not request.user.is_authenticated:
                return redirect('login')
        else:
            product = Product.objects.get(id=product_id)
            weight=request.POST.get('weightlist')
                
            try:
                weight = float(weight)
            except ValueError:
                messages.error(request, 'Please select a valid weight/piece') 
                return redirect('product_detail',product_id=product_id)
                
            varient=Variation.objects.get(product=product,weight=weight)
            
            if varient.stock > 0: 
                price = varient.get_price()
                        
                cart_item,created=CartItem.objects.get_or_create(user_id=request.user.id,variations=varient,discounted_price=price)
                        
                if not created:
                    if varient.stock >= cart_item.quantity + 1:
                            cart_item.quantity += 1
                            cart_item.save()

                    
            else:
                messages.error(request, "Sorry, this item is out of stock.")            
                    
            return redirect('cart')  
    return redirect('cart')
     

  
def shop_cart(request):
  
    try:
        total = 0
        quantity = 0
        cart_items = [] 
        
        cart_items=CartItem.objects.filter(user_id=request.user)

        applied_coupon = request.session.get('applied_coupon')

        for cart_item in cart_items:
            # if cart_item.variations:
            #     price =  cart_item.variations.price
            #     weight = cart_item.variations.weight
           
            total+= (cart_item.subtotal)
            
            quantity+=(cart_item.quantity)

        if applied_coupon:
            try:
                
                coupon = Coupon.objects.get(code=applied_coupon,users=request.user)
                if not coupon.is_expired():

                   discount_amount = (total * coupon.discount_percentage) / 100
                   total -= discount_amount
                else:
                    messages.warning(request, "The applied coupon has expired.")
                    del request.session['applied_coupon'] 


            except Coupon.DoesNotExist:
                messages.warning(request, "The applied coupon is no longer valid.")
                del request.session['applied_coupon'] 
    except  :
        pass
    context ={
       'total':total,
       'quantity':quantity,
       'cart_items':cart_items,

    }

    return render(request,"shop-cart.html",context)


def delete_cart(request,cart_id):
    cart=CartItem.objects.get(id=cart_id)
    cart.delete()
   
    return redirect(shop_cart)

def order(request):
    
    addresses=ShippingAddress.objects.filter(user=request.user).order_by('-id')
    if addresses.exists():
        last_added_address = addresses.first()
    else:
        last_added_address = None
    cartitems = CartItem.objects.filter(user_id=request.user,status=False)
    total = 0
    selected_address = None
    
    applied_coupon = request.session.get('applied_coupon')
       
    for cartitem in cartitems:
        total += cartitem.subtotal
    if applied_coupon:
        try:
                coupon = Coupon.objects.get(code=applied_coupon, users=request.user)
                discount_amount = (total * coupon.discount_percentage) / 100
                total -= discount_amount

        except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
                return redirect('order')
        
      
          
        
    if not cartitems.exists(): 
            return render(request,'shop-cart.html')
   
    if request.method=="POST":
        total=0
        item_list=[]

        for cartitem in cartitems:
            total += cartitem.subtotal

            item=OrderItems.objects.create(
            quantity=cartitem.quantity,
            sub_total=cartitem.subtotal,
            variant=cartitem.variations,)
            item_list.append(item)

        if applied_coupon:
            try:
                coupon = Coupon.objects.get(code=applied_coupon, users=request.user)
                discount_amount = (total * coupon.discount_percentage) / 100
                total -= discount_amount

            except Coupon.DoesNotExist:
               messages.error(request, "Invalid coupon code.")
               return redirect('order')
       
        
        # if 'selected_address' not in request.POST:
        #     messages.error(request, "Please select an address.")
        #     return redirect('order')
        
        address_id=request.POST["selected_address"]
        selected_address=ShippingAddress.objects.get(id=address_id)
        payment_method=request.POST["payment_option"]
        order_notes=request.POST["order_notes"]

       
        #storing
        request.session['item_list'] = [item.id for item in item_list]
        request.session['selected_address'] = selected_address.id
        request.session['payment_method'] = payment_method
        request.session['order_notes'] = order_notes
        request.session['total'] =str( total)
        #ok

        if payment_method=="razorpay":
            total=total*100
            client = razorpay.Client(auth=("rzp_test_xlthjADEQlar19", "6hDaXQaAuJPgir4dexh95N6M"))

            DATA = {
                "amount": int(total),
                "currency": "INR",
                "payment_capture":'1'
                
            }
            client.order.create(data=DATA)

            return render(request,"razorpay.html", {"total":total})    
          
        elif payment_method=="pay_with_wallet":
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance < total:
                messages.error(request, "Insufficient balance in your wallet.")
                return redirect('order')

           
            wallet.balance -= total
            wallet.save()
            return redirect(create_order)
        
        else:

            order=Order.objects.create(
                    user=request.user,
                    full_name=selected_address.full_name,
                    address=selected_address.address,
                    phone_number=selected_address.phone_number,
                    city=selected_address.city,
                    district=selected_address.district,
                    pincode=selected_address.pincode,
                    payment_method=payment_method,
                    order_notes=order_notes,
                    bill_amount=total,
                    status="confirmed"
                                        
                )
            for value in item_list:
                order.new_order.add(value)

            for cartitem in cartitems:
                variation = cartitem.variations
                variation.stock -= cartitem.quantity
                variation.save()

            cartitems.delete()
            
            cartitems = CartItem.objects.filter(user_id=request.user, status=False)
            if 'applied_coupon' in request.session:
               del request.session['applied_coupon']
            
            return redirect('success')
    
    return render(request,'shop-checkout.html',{'address':addresses,'cartitems':cartitems, 'total':total,'selected_address':selected_address,'last_added_address': last_added_address})

def new_address(request):
    cartitems = CartItem.objects.filter(user_id=request.user, status=False)
    
    if request.method=="POST":
        fullname = request.POST.get('fullname')
        address = request.POST.get('address')
        district = request.POST.get('district')
        city = request.POST.get('city')
        phonenumber = request.POST.get('phonenumber')
        pincode = request.POST.get('pincode')
        
        if not (fullname and address and district and city and phonenumber and pincode):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'shop-checkout.html', {'cartitems': cartitems})


        valid=True

        if not fullname.isalpha():
            messages.error(request,"Full name should contain only alphabetic characters")
            valid = False

        if not city.isalpha():
            messages.error(request,"City should contain only alphabetic characters")
            valid = False

        if not pincode.isdigit() or len(pincode) != 6:
             messages.error(request,"Pincode should be a 6-digit number")
             valid = False

        if not phonenumber.isdigit() or len(phonenumber) != 10:
            messages.error(request,"Phone number should be a 10-digit number")
            valid = False

        if address.isdigit() :
            messages.error(request,"Address should contain text ")
            valid = False
        
        if valid:
            
            user=request.user

            shipping_address= ShippingAddress.objects.create(user=user,
            full_name=fullname,address=address,city=city,district=district,
            pincode=pincode,phone_number=phonenumber)
            
            
    
   
    return redirect(order)

def update_quantity(request):
   
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
   
        item_id = request.POST.get('item_id')
       
        is_increase = request.POST.get('increase') 

        cart_item = CartItem.objects.get(id=item_id)
        variation_price = cart_item.variations.price

        is_increase = is_increase.lower() == 'true'

        if is_increase :
            if cart_item.quantity + 1 <= cart_item.variations.stock:
                cart_item.quantity += 1
           
            
        else:
            cart_item.quantity -= 1 if cart_item.quantity > 1 else 0
        
        if cart_item.quantity > cart_item.variations.stock:
                return JsonResponse({'error': 'Exceeds available stock'})

        cart_item.subtotal = cart_item.quantity * variation_price
        
        cart_item.save()
        
       
     
     
        
        return JsonResponse({'quantity': cart_item.quantity,'subtotal':cart_item.subtotal})
    return JsonResponse({'error': 'Invalid request'})




def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
     
        if 'applied_coupon' in request.session:
            messages.warning(request, "A coupon is already applied.")
            return redirect('cart')

        try:
           
            coupon = Coupon.objects.get(
                code=coupon_code,
                expiry_date__gte=timezone.now().date(),
               
            )
            user = request.user
            
           
            if user not in coupon.users.all():
            
                coupon.users.add(user)  
                 
                coupon.save()
                request.session['applied_coupon'] = coupon_code
                messages.success(request, "Coupon applied successfully.")
            else:
                messages.error(request, 'Coupon already used by this user.')

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return redirect('cart')


def success(request):

    return render(request,"success.html")



def create_order(request):
    cartitems = CartItem.objects.filter(user_id=request.user,status=False)

    item_list_ids = request.session.get('item_list', [])
    selected_address_id = request.session.get('selected_address')
    payment_method = request.session.get('payment_method')
    order_notes = request.session.get('order_notes')
    total =Decimal (request.session.get('total', 0))

    item_list = OrderItems.objects.filter(id__in=item_list_ids)
    selected_address = ShippingAddress.objects.get(id=selected_address_id)

    order=Order.objects.create(
        user=request.user,
        full_name=selected_address.full_name,
        address=selected_address.address,
        phone_number=selected_address.phone_number,
        city=selected_address.city,
        district=selected_address.district,
        pincode=selected_address.pincode,
        payment_method=payment_method,
        order_notes=order_notes,
        bill_amount=total,
        status="confirmed"
                                        
        )
    for value in item_list:
        order.new_order.add(value)

    for cartitem in cartitems:
        variation = cartitem.variations
        variation.stock -= cartitem.quantity
        variation.save()
            
        cartitems.delete()
            
        cartitems = CartItem.objects.filter(user_id=request.user, status=False)
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

    return redirect (success)