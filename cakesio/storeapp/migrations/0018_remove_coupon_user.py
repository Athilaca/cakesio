# Generated by Django 4.2.4 on 2023-12-02 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0017_coupon_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='user',
        ),
    ]
