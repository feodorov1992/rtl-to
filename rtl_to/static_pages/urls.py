from django.urls import path

from static_pages.views import home_view

urlpatterns = [
    path('', home_view, name='home'),
]
