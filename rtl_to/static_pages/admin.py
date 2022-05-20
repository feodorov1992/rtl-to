from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import MainTextBlock


@admin.register(MainTextBlock)
class MainPageAdmin(ModelAdmin):
    pass
