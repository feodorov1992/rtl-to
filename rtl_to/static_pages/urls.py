from django.urls import path

from static_pages.views import home_view, requisites, price_list

urlpatterns = [
    path('', home_view, name='home'),
    path('requisites/', requisites, name='requisites'),
    path('price/', price_list, name='price_list'),
]
