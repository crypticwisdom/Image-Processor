# Generated by Django 4.0.1 on 2022-02-03 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_store_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
