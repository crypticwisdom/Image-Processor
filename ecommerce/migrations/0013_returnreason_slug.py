# Generated by Django 4.0.1 on 2022-11-09 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0012_returnreason_orderproduct_sub_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnreason',
            name='slug',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
