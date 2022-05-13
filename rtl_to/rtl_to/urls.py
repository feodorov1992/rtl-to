from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('static_pages.urls')),
    path('admin/', admin.site.urls),
    path('profile/', include('app_auth.urls')),
    path('management/', include('management.urls')),
    path('clientsarea/', include('clientsarea.urls')),
]
