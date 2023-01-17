from django.contrib import admin
from .models import ApplicationExtension, ApplicationContentType
# Register your models here.

admin.site.register(ApplicationExtension)
admin.site.register(ApplicationContentType)
