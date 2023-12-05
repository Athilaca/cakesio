
from import_export import resources
from storeapp.models import Order

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'user__first_name', 'created_date', 'bill_amount', 'payment_method')
        export_order = ('id', 'user__first_name', 'created_date', 'bill_amount', 'payment_method')
        widgets = {
            'created_date': {'format': '%Y-%m-%d'},
        }

