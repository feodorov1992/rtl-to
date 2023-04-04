from django.shortcuts import render, get_object_or_404
from static_pages.models import MainTextBlock, Vacancy


def home_view(request):
    """
    Главная страница
    """
    blocks = MainTextBlock.objects.all()
    return render(request, 'static_pages/home.html', {'blocks': blocks})


def vacancy_detail(request, pk):
    """
    Просмотр вакансии
    """
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'static_pages/vacancy_detail.html', {'vacancy': vacancy})


def vacancies_list(request):
    """
    Список вакансий
    """
    vacancies = Vacancy.objects.all()
    return render(request, 'static_pages/vacancies_list.html', {'vacancies': vacancies})
