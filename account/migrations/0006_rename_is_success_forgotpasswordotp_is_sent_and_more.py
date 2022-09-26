# Generated by Django 4.0.1 on 2022-09-11 09:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_rename_forgotpassword_forgotpasswordotp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forgotpasswordotp',
            old_name='is_success',
            new_name='is_sent',
        ),
        migrations.AddField(
            model_name='forgotpasswordotp',
            name='expired',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 11, 10, 52, 35, 712007), help_text='Expires after 5 minutes'),
        ),
    ]
