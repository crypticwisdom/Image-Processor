# Generated by Django 4.0.1 on 2022-02-03 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_productcategory_brands'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='brands',
            field=models.ManyToManyField(blank=True, related_name='brands', to='store.Brand'),
        ),
    ]
