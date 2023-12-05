# Generated by Django 4.2.4 on 2023-11-15 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0008_alter_variation_weight'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_percentage', models.PositiveIntegerField()),
                ('expiry_date', models.DateField()),
            ],
        ),
    ]
