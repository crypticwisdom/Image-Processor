# Generated by Django 4.0.1 on 2022-09-20 07:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0022_alter_forgotpasswordotp_expire_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgotpasswordotp',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 20, 7, 26, 7, 443392, tzinfo=utc), help_text='Expires after 5 minutes'),
        ),
    ]
