# Generated by Django 4.0.1 on 2022-09-11 10:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_forgotpasswordotp_expire_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgotpasswordotp',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 11, 11, 49, 37, 586356), help_text='Expires after 5 minutes'),
        ),
    ]
