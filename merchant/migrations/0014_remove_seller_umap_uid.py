# Generated by Django 4.0.1 on 2022-11-30 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0013_seller_umap_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='umap_uid',
        ),
    ]
