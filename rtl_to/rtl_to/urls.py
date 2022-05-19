from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include
from django.views.generic import RedirectView

from rtl_to import settings

urlpatterns = [
    path('', include('static_pages.urls')),
    path('admin/', admin.site.urls),
    path('profile/', include('app_auth.urls')),
    path('management/', include('management.urls')),
    path('clientsarea/', include('clientsarea.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
