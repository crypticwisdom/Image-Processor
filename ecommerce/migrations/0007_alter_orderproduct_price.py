# Generated by Django 4.0.1 on 2022-10-21 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_order_remove_cartbill_shipper_cartbill_shipper_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50),
        ),
    ]
