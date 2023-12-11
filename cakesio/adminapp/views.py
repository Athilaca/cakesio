from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from cakeapp.models import CustomUser
from django.core.exceptions import ValidationError
from adminapp.models import *
from storeapp.models import *
from datetime import datetime
from django.db.models import Sum,Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .resources import OrderResource
from django.http import JsonResponse
from django.core.serializers import serialize





# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect(admin_dashboard)         
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
            return redirect(admin_login)
    return render(request, 'page-account-login.html')


@login_required(login_url='adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    
        total_orders = Order.objects.count()
        total_amount = Order.objects.aggregate(total_amount=Sum('bill_amount'))['total_amount'] or 0
        total_products = Product.objects.count()
        total_users = CustomUser.objects.count()
        total_categories = Category.objects.count()
        current_month = timezone.now().month
        current_year = timezone.now().year
    
    
        monthly_sales_sum = Order.objects.filter(created_date__month=current_month).aggregate(monthly_sales=Sum('bill_amount'))['monthly_sales'] or 0
        yearly_sales_sum = Order.objects.filter(created_date__year=current_year).aggregate(yearly_sales=Sum('bill_amount'))['yearly_sales'] or 0

        
        
        context = {
            'total_orders': total_orders,
            'total_amount': total_amount,
            'total_products': total_products,
            'total_users': total_users,
            'total_categories': total_categories,
            'monthly_sales': monthly_sales_sum,
            'yearly_sales': yearly_sales_sum,
        }
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
           return JsonResponse(context)
    
       
        return render(request, 'page-dashboard.html', context)

    
   

@login_required(login_url='adminlogin')
def admin_user(request):
   
    data=CustomUser.objects.all()
  
    return render(request,'page-user.html',{'data':data})
       


def block_user(request, user_id):

        user = CustomUser.objects.get(id=user_id)
    
        user.is_active = False  # Block the user by setting is_active to False
        user.save()
       
        return redirect(admin_user)
    
def unblock_user(request, user_id):
   
        user = CustomUser.objects.get(id=user_id)
        user.is_active = True  
        user.save()
       
        return redirect(admin_user)


@login_required(login_url='adminlogin') 
def admin_category(request):
        data=Category.objects.all()
    
        if request.method=='POST':
            try:
            
                name=request.POST.get("name")
                slug=request.POST.get("slug")
                description=request.POST.get("description")
                category_image=request.FILES.get('category_image')
                
                if not name or not slug:
                    raise ValidationError("Name and Slug are required fields.")
                if Category.objects.filter(Q(slug=slug) | Q(category_name=name)).exists():
                     raise ValidationError("Category with the same name or slug already exists.")
                if not category_image:
                    raise ValidationError("Please upload an image.")
                
            except (ValueError, ValidationError) as e:
                error_message = str(e)  
                return render(request,'page-categories.html',{'datas':data,'error_message': error_message,})  
        
            myuser=Category(category_name=name,slug=slug,description=description,category_image=category_image)
            myuser.save()
            
        
        
            return redirect('admin_category')
            
        return render(request,'page-categories.html',{'datas':data})


def admin_editcategory(request,id):
    if request.user.is_authenticated:

        category_object=Category.objects.get(id=id)

        if request.method == 'POST':
            name=request.POST.get("name")
            slug=request.POST.get("slug")
            description=request.POST.get("description")
            category_image=request.FILES.get('category_image')
        
            category_object.category_name= name
            category_object.slug=slug
            category_object.description=description
            category_object.category_image=category_image
            category_object.save()
            
            return redirect('admin_category')


    return render(request,'page-editcategory.html',{'datas':category_object})

@login_required(login_url='adminlogin')
def admin_product(request):
    
    data=Product.objects.all()

    return render(request,'page-products.html',{"datas":data})

@login_required(login_url='adminlogin')    
def admin_addproduct(request):
   
    categories=Category.objects.all()
    seasonal_offer=SeasonalOffer.objects.all()
    if request.method=="POST":
        try:
            product_name=request.POST.get("product_name")
            description=request.POST.get("description")
            price=request.POST.get("price")
            images=request.FILES.get("images")
            
            oldprice=request.POST.get("oldprice")
            front_image=request.FILES.get("front_image") 
            top_image=request.FILES.get("top_image")
            category=request.POST.get("category")
            seasonal_offer=request.POST.get('seasonal_offer')
            if not product_name or not description:
               raise ValidationError( "Product Name and description are required fields.")
           
            if int(price) < 0:
                raise ValidationError("Price must be a positive value.")
            
            if int(oldprice) < 0:
                raise ValidationError("Old price must be a positive value.")
            if not images and not front_image and not top_image:
                raise ValidationError("Please upload an image.")
           
        except (ValueError, ValidationError) as e:
            error_message = str(e)
            return render(request, 'page-addproduct.html', {'error_message': error_message,'category':categories,'seasonal_offer':seasonal_offer})
        
        category = Category.objects.get(id=category)
        seasonal_offer=SeasonalOffer.objects.get(id=seasonal_offer)
        myuser=Product(product_name=product_name,description=description,price=price,images=images,oldprice=oldprice,
        front_image=front_image,top_image=top_image,category=category,seasonal_offer=seasonal_offer)
        myuser.save()
      
        return redirect('admin_product')
    return render(request, 'page-addproduct.html', {'category':categories,'seasonal_offer':seasonal_offer})



def admin_editproduct(request,id):
    category=Category.objects.all()
    Product_object=Product.objects.get(id=id)

    if request.method == 'POST':
        product_name=request.POST.get("product_name")
        description=request.POST.get("description")
        images=request.FILES.get("images")
        stock=request.POST.get("stock")
        oldprice=request.POST.get("oldprice")
        front_image=request.FILES.get("front_image") 
        top_image=request.FILES.get("top_image")
        is_seasonal = request.POST.get("seasonal") == "on" 

        if images:
            Product_object.images=images
        if top_image :
            Product_object.top_image=top_image
        if front_image :
            Product_object.front_image=front_image
      
        Product_object.product_name= product_name
        Product_object.description=description
        Product_object.stock=stock
        Product_object.oldprice=oldprice
        Product_object.is_seasonal =is_seasonal
        
    
        Product_object.save()
        
        return redirect('admin_product')


    return render(request,'page-addproduct.html',{'datas':Product_object,'category':category})

def product_delete(request,id):
        product=Product.objects.get(id=id)

        if product.is_deleted:
       
           product.is_deleted = False
        else:
           product.soft_delete()
        product.save() 
          
        return redirect(admin_product)
      
def category_delete(request,id):
   
        dele=Category.objects.get(id=id)
      
        dele.delete()
        return redirect(admin_category)

@login_required(login_url='adminlogin') 
def admin_logout(request):
    
    logout(request)
       
    return redirect(admin_login)

   
@login_required(login_url='adminlogin') 
def admin_orders(request):
    status = request.GET.get('status', 'none')

    if status == 'none':
        orders = Order.objects.all().select_related('user').order_by('-id')
    else:
        orders = Order.objects.filter(status=status).select_related('user').order_by('-id')

    return render(request,'page-orders.html',{"orders":orders})


def order_details(request,order_id):
    
    order_details=Order.objects.get(id=order_id)
    order_items=Order.objects.get(id=order_id).new_order.all().select_related('variant')
    if request.method=="POST":
        status=request.POST.get("status")
       
        order_details.status = status
        order_details.save()
    
    context={'order_items':order_items,'order_details':order_details}

    return render (request,'page-orderdetails.html',context)

@login_required(login_url='adminlogin')     
def banner(request):

    banner=Banner.objects.first()
    return render(request,'page-banner.html',{'banner':banner})   
 

def admin_editbanner(request,id):

    banner_object, created = Banner.objects.get_or_create(pk=id)
    if request.method == 'POST':
        banner_object.banner1 = request.FILES.get("banner1") or banner_object.banner1
        banner_object.banner2 = request.FILES.get("banner2") or banner_object.banner2
        banner_object.banner3 = request.FILES.get("banner3") or banner_object.banner3
        banner_object.offer_banner1 = request.FILES.get("offer_banner1") or banner_object.offer_banner1
        banner_object.offer_banner2 = request.FILES.get("offer_banner2") or banner_object.offer_banner2
        banner_object.offer_banner3 = request.FILES.get("offer_banner3") or banner_object.offer_banner3

        banner_object.save()
        return redirect('banners')  # Replace 'banner' with the actual URL name for the banners page

    return render(request, 'page-editbanner.html', {'banner': banner_object})



def sales_report(request):
   
    selected_date_str = request.GET.get('selected_date')
    end_date_str = request.GET.get('end_date')
    
    context = {}
    
    if selected_date_str:
        
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
           
        daily_sales = Order.objects.filter(created_date__date=selected_date).order_by('-id')
        weekly_sales = Order.objects.filter(created_date__week=selected_date.isocalendar()[1]).order_by('-id')
        daily_total_sales = daily_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales'] or 0
        weekly_total_sales = weekly_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales']or 0
      
        if selected_date_str and end_date_str:
       
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            orders_in_date_range = Order.objects.filter(created_date__range=(selected_date, end_date)).order_by('-id')
            total_sales_in_date_range = orders_in_date_range.aggregate(total_sales=Sum('bill_amount'))['total_sales'] or 0

            context = {
                  
                    'selected_date': selected_date_str,
                    'end_date': end_date_str,
                    'orders_in_date_range': orders_in_date_range,
                    'total_sales_in_date_range': total_sales_in_date_range
            }
            if 'export' in request.GET:
                print("Export button clicked!")
                resource = OrderResource()
                dataset = resource.export(orders_in_date_range)

                    # Create a response object.
                response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'

                return response
        
        else:

            context = {
                    
                    'daily_sales': daily_sales,
                    'weekly_sales': weekly_sales,
                    'daily_total_sales': daily_total_sales,
                    'weekly_total_sales': weekly_total_sales,
                    'selected_date': selected_date_str,
                    'end_date': end_date_str,
            }

       
       
            
    return render(request, 'page-salesreport.html', context)

@login_required(login_url='adminlogin') 
def product_variation(request):
    
    variations=Variation.objects.all()
    product=Product.objects.all()
  
    if request.method=="POST":
        try:
            product_name=request.POST.get("product_name")
            weight=request.POST.get("weight")
            price=request.POST.get("price")
           
            stock=request.POST.get("stock")

            if not product_name :
               raise ValidationError( "Product Name is required.")
           
            if int(price) < 0:
                raise ValidationError("Price must be a positive value.")
            
            if int(weight) < 0:
                raise ValidationError("weight must be a positive value.")
            
            if int(stock) < 0:
                raise ValidationError("Stock must be a non-negative integer.")
   
        except (ValueError, ValidationError) as e:
            error_message = str(e)
            return render(request, 'page-addproduct.html', {'error_message': error_message})
        
        product = Product.objects.get(id=product_name)
        myuser=Variation(product=product,price=price,stock=stock,weight=weight)
        myuser.save()

      
        return redirect('product_variation')
    return render(request,'page-variation.html',{'product':product,'variations':variations}) 
   
@login_required(login_url='adminlogin') 
def coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount_percentage = request.POST.get('discount_percentage')
        expiry_date = request.POST.get('expiry_date')
   
        try:
           
            discount_percentage = int(discount_percentage)
            
            
            expiry_date = timezone.datetime.strptime(expiry_date, '%Y-%m-%d').date()

           
            coupon = Coupon.objects.create(
                user=request.user,
                code=coupon_code,
                discount_percentage=discount_percentage,
                expiry_date=expiry_date
            )
        except ValueError:
            return HttpResponse('Invalid discount percentage or expiry date format.') 
           
    return render(request,'page-coupon.html')

