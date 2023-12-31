# Generated by Django 4.2.4 on 2023-11-09 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storeapp', '0002_remove_cartitem_product_cartitem_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=15)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=6)),
                ('unlisted', models.BooleanField(default=False)),
                ('payment_method', models.CharField(max_length=50)),
                ('order_notes', models.CharField(max_length=50)),
                ('bill_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('new_order', models.ManyToManyField(to='storeapp.orderitems')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
