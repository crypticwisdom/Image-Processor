# Generated by Django 4.0.1 on 2022-11-17 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_profile_verification_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='wallet_id',
        ),
        migrations.AddField(
            model_name='profile',
            name='pay_auth',
            field=models.TextField(blank=True, null=True),
        ),
    ]
