from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('account/', include('account.urls')),
    path('store/', include('store.urls')),
    path('seller/', include('merchant.urls')),
    path('location/', include('location.urls')),
    path('superadmin/', include('superadmin.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('admin/', admin.site.urls),
]
