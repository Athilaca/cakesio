# Generated by Django 4.2.4 on 2023-12-01 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0016_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]