# Generated by Django 4.1.3 on 2022-12-15 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_validatorblock_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='validatorblock',
            name='numb_of_images_per_process',
            field=models.PositiveSmallIntegerField(blank=True, default=1, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='validatorblock',
            name='file_threshold_size',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Any file size above this threshold will be rejected. Sizes are converted to KB.', max_digits=10),
        ),
    ]
