from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import MainTextBlock, Requisite, Position


@admin.register(MainTextBlock)
class MainPageAdmin(ModelAdmin):
    pass


@admin.register(Requisite)
class RequisitesAdmin(ModelAdmin):
    pass


@admin.register(Position)
class PriceListAdmin(ModelAdmin):
    pass
