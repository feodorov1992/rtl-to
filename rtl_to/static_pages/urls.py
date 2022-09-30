from django.urls import path

from static_pages.views import home_view, vacancies_list, vacancy_detail

urlpatterns = [
    path('', home_view, name='home'),
    path('vacancies/', vacancies_list, name='vacancies_list'),
    path('vacancies/<int:pk>', vacancy_detail, name='vacancy_detail')
]
