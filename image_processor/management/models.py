from django.db import models

# Create your models here.


class ApplicationExtension(models.Model):
    extension_name = models.CharField(max_length=10, help_text="List of extension available on the platform. e.g .png")

    def __str__(self):
        return self.extension_name


class ApplicationContentType(models.Model):
    content_name = models.CharField(max_length=30, help_text="List of content-type available on the "
                                                             "platform. e.g image/png")

    def __str__(self):
        return self.content_name
