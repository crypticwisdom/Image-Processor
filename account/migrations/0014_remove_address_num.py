# Generated by Django 4.0.1 on 2022-12-15 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_remove_profile_billing_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='num',
        ),
    ]
