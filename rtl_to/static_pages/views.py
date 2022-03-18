from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from app_auth.models import User


def home_view(request):
    return render(request, 'static_pages/home.html', {})
