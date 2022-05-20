from django.shortcuts import render
from static_pages.models import MainTextBlock


def home_view(request):
    blocks = MainTextBlock.objects.all()
    return render(request, 'static_pages/home.html', {'blocks': blocks})
