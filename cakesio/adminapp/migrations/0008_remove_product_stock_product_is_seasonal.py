# Generated by Django 4.2.4 on 2023-11-23 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0007_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='product',
            name='is_seasonal',
            field=models.BooleanField(default=False),
        ),
    ]
