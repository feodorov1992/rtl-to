from django.contrib import admin
from django.contrib.admin import ModelAdmin

from orders.models import TransitHistory


@admin.register(TransitHistory)
class TransitHistoryAdmin(ModelAdmin):
    pass
