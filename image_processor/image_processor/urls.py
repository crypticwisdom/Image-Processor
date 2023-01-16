from django.contrib import admin
from django.urls import path, include
from account.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('processor/', include('processor.urls')),
]
