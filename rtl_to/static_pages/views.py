from django.shortcuts import render
from static_pages.models import MainTextBlock, Vacancy


def home_view(request):
    blocks = MainTextBlock.objects.all()
    return render(request, 'static_pages/home.html', {'blocks': blocks})


def vacancy_detail(request, pk):
    vacancy = Vacancy.objects.get(pk=pk)
    return render(request, 'static_pages/vacancy_detail.html', {'vacancy': vacancy})


def vacancies_list(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'static_pages/vacancies_list.html', {'vacancies': vacancies})
