# Generated by Django 5.0.6 on 2024-06-07 17:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.RegexValidator('^[0-9]+$', 'Enter a Valid Phone Number.')]),
        ),
    ]
