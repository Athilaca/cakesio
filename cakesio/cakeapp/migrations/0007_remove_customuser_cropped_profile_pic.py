# Generated by Django 4.2.4 on 2023-11-19 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cakeapp', '0006_customuser_cropped_profile_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='cropped_profile_pic',
        ),
    ]