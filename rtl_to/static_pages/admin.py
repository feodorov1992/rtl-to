from django.contrib import admin
from django.contrib.admin import ModelAdmin
from static_pages.models import MainTextBlock, Vacancy


@admin.register(MainTextBlock)
class MainPageAdmin(ModelAdmin):
    pass


@admin.register(Vacancy)
class VacancyAdmin(ModelAdmin):
    pass
