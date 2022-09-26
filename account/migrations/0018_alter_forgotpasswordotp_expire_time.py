# Generated by Django 4.0.1 on 2022-09-18 13:45

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_alter_forgotpasswordotp_expire_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgotpasswordotp',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 18, 13, 50, 9, 392120, tzinfo=utc), help_text='Expires after 5 minutes'),
        ),
    ]
