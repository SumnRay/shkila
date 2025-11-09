
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('accounts.api_urls', namespace='accounts_api')),
    path('', include('accounts.urls', namespace='accounts')),
]
