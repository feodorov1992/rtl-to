from django.contrib import admin
from django.contrib.admin import ModelAdmin

from orders.models import Order, Transit, Cargo, ExtraCargoParams, ExtraService, OrderHistory, \
    TransitSegment, TransitHistory


@admin.register(OrderHistory)
class ContractorAdmin(ModelAdmin):
    pass


@admin.register(TransitHistory)
class TransitHistoryAdmin(ModelAdmin):
    pass


@admin.register(TransitSegment)
class ContractorAdmin(ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    pass


@admin.register(Transit)
class TransitAdmin(ModelAdmin):
    pass


@admin.register(Cargo)
class CargoAdmin(ModelAdmin):
    pass


@admin.register(ExtraCargoParams)
class ExtraCargoParamsAdmin(ModelAdmin):
    pass


@admin.register(ExtraService)
class ExtraServiceAdmin(ModelAdmin):
    pass
