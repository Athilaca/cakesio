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
from chartjs.views.lines import BaseLineChartView
from .resources import OrderResource
from django.http import JsonResponse

from io import BytesIO
# from .resources import OrderResource


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect(admin_index)         
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
            return redirect(admin_login)
    return render(request, 'page-account-login.html')


@login_required(login_url='adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_index(request):
    
        total_orders = Order.objects.count()
        total_amount = Order.objects.aggregate(total_amount=Sum('bill_amount'))['total_amount'] or 0
        total_products = Product.objects.count()
        total_users = CustomUser.objects.count()
        total_categories = Category.objects.count()
        
        
        context = {
            'total_orders': total_orders,
            'total_amount': total_amount,
            'total_products': total_products,
            'total_users': total_users,
            'total_categories': total_categories,
        }
        
        
        return render(request, 'page-index.html', context)

    
   


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
                
                if not name or not slug:
                    raise ValidationError("Name and Slug are required fields.")
                if Category.objects.filter(Q(slug=slug) | Q(category_name=name)).exists():
                     raise ValidationError("Category with the same name or slug already exists.")

            except (ValueError, ValidationError) as e:
                error_message = str(e)  
                return render(request,'page-categories.html',{'datas':data,'error_message': error_message,})  
        
            myuser=Category(category_name=name,slug=slug,description=description)
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
        
            category_object.category_name= name
            category_object.slug=slug
            category_object.description=description
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
    if request.method=="POST":
        try:
            product_name=request.POST.get("product_name")
            description=request.POST.get("description")
            price=request.POST.get("price")
            images=request.FILES.get("images")
            stock=request.POST.get("stock")
            oldprice=request.POST.get("oldprice")
            front_image=request.FILES.get("front_image") 
            top_image=request.FILES.get("top_image")
            category=request.POST.get("category")

            if not product_name or not description:
               raise ValidationError( "Product Name and description are required fields.")
           
            if int(price) < 0:
                raise ValidationError("Price must be a positive value.")
            
            if int(oldprice) < 0:
                raise ValidationError("Old price must be a positive value.")
            if not images or not front_image or not top_image:
                raise ValidationError("Please upload an image.")
            if int(stock) < 0:
                raise ValidationError("Stock must be a non-negative integer.")
   
        except (ValueError, ValidationError) as e:
            error_message = str(e)
            return render(request, 'page-addproduct.html', {'error_message': error_message,'category':categories})
        
        category = Category.objects.get(id=category)
        myuser=Product(product_name=product_name,description=description,price=price,images=images,stock=stock,oldprice=oldprice,front_image=front_image,top_image=top_image,category=category)
        myuser.save()
      
        return redirect('admin_product')
    return render(request, 'page-addproduct.html', {'category':categories})



def admin_editproduct(request,id):

    Product_object=Product.objects.get(id=id)

    if request.method == 'POST':
        product_name=request.POST.get("product_name")
        description=request.POST.get("description")
        images=request.FILES.get("images")
        stock=request.POST.get("stock")
        oldprice=request.POST.get("oldprice")
        front_image=request.FILES.get("front_image") 
        top_image=request.FILES.get("top_image")        
        if images:
            Product_object.images=images
             
        if top_image:
            Product_object.top_image=top_image
        if front_image:
            Product_object.front_image=front_image
      
        Product_object.product_name= product_name
        Product_object.description=description
        Product_object.stock=stock
        Product_object.oldprice=oldprice
        
    
        Product_object.save()
        
        return redirect('admin_product')


    return render(request,'page-addproduct.html',{'datas':Product_object})

def product_delete(request,id):
   
        product=Product.objects.get(id=id)
      
        product.soft_delete()
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
    
    order=Order.objects.all().select_related('user').order_by('-id')
    return render(request,'page-orders.html',{"orders":order})


def order_details(request,order_id):
    
    order_details=Order.objects.get(id=order_id)
    order_items=Order.objects.get(id=order_id).new_order.all().select_related('variant')
    if request.method=="POST":
        status=request.POST.get("status")
       
        order_details.status = status
        order_details.save()
    
    context={'order_items':order_items,'order_details':order_details}

    return render (request,'page-orderdetails.html',context)
    
def banner(request):
    if request.method=="POST":
        image=request.FILES.get("banner")   
        banner=Banner(banner=image)
        banner.save() 

    return render(request,'page-blank.html')    




def sales_report(request):
   
    selected_date_str = request.GET.get('selected_date')
    
   
   
    context = {}
    
    if selected_date_str:
        
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        
    
           
        daily_sales = Order.objects.filter(created_date__date=selected_date).order_by('-id')
        weekly_sales = Order.objects.filter(created_date__week=selected_date.isocalendar()[1]).order_by('-id')
        monthly_sales = Order.objects.filter(created_date__month=selected_date.month)
        yearly_sales = Order.objects.filter(created_date__year=selected_date.year).order_by('-id')
        
       
           
        daily_total_sales = daily_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales'] or 0

        weekly_total_sales = weekly_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales']or 0
        monthly_total_sales = monthly_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales']
        yearly_total_sales = yearly_sales.aggregate(total_sales=Sum('bill_amount'))['total_sales']

        context = {
                'daily_sales': daily_sales,
                'weekly_sales': weekly_sales,
                'monthly_sales': monthly_sales,
                'yearly_sales': yearly_sales,
                'daily_total_sales': daily_total_sales,
                'weekly_total_sales': weekly_total_sales,
                'monthly_total_sales': monthly_total_sales,
                'yearly_total_sales': yearly_total_sales,
                'selected_date': selected_date,
        }

        if 'export' in request.GET:
            # Create a resource and export the queryset
           

            resource = OrderResource()
            dataset = resource.export(yearly_sales)

                # Create a response object.
            response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'

            return response
       
            
    return render(request, 'page-salesreport.html', context)

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
           
    return render(request,'page-blank.html')

# class SalesChartDataView(View):
#     def get(self, request, *args, **kwargs):
#         sales_data = Order.objects.values('created_date__month').annotate(total_sales=models.Sum('bill_amount'))
#         labels = [entry['created_date__month'] for entry in sales_data]
#         data = [entry['total_sales'] for entry in sales_data]

#         chart_data = {
#             'labels': labels,
#             'datasets': [{
#                 'label': 'Total Sales',
#                 'data': data,
#                 'backgroundColor': 'rgba(75, 192, 192, 0.2)',
#                 'borderColor': 'rgba(75, 192, 192, 1)',
#                 'borderWidth': 1,
#                 }]
#         }

#         return JsonResponse(chart_data)

# class SalesChartView(BaseLineChartView):
#     def get_labels(self):
#         sales_data = Order.objects.values('created_date__month').annotate(total_sales=models.Sum('bill_amount'))
#         return [entry['created_date__month'] for entry in sales_data]

#     def get_providers(self):
#         return ['Total Sales']

#     def get_data(self):
#         sales_data = Order.objects.values('created_date__month').annotate(total_sales=models.Sum('bill_amount'))
#         return [[entry['total_sales'] for entry in sales_data]]

# def sales_chart(request):
#     return render(request, 'sales_chart.html')
