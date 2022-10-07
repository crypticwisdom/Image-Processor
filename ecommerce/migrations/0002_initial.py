# Generated by Django 4.0.1 on 2022-09-26 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecommerce', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.store'),
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce.productcategory'),
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.cart'),
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='product_detail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.productdetail'),
        ),
        migrations.AddField(
            model_name='cartbill',
            name='cart',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.cart'),
        ),
        migrations.AddField(
            model_name='cartbill',
            name='shipper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerce.shipper'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
