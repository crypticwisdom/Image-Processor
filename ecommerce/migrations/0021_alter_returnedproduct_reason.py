# Generated by Django 4.0.1 on 2022-11-24 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0020_alter_returnproductimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnedproduct',
            name='reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce.returnreason'),
        ),
    ]
