from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from app_auth.models import User
from static_pages.models import MainTextBlock, Requisite, Position


def home_view(request):
    blocks = MainTextBlock.objects.all()
    return render(request, 'static_pages/home.html', {'blocks': blocks})


def requisites(request):
    requs = Requisite.objects.all()
    return render(request, 'static_pages/requisites.html', {'requisites': requs})


def price_list(request):
    poses = Position.objects.all()
    return render(request, 'static_pages/price_list.html', {'poses': poses})
