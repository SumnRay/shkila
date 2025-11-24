
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('accounts.api_urls', namespace='accounts_api')),
    path('', include('accounts.urls', namespace='accounts')),
    path('api/admin/', include('sk.admin_api_urls')),
    path('api/manager/', include('sk.manager_api_urls')),
]
