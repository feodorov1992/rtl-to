from django.urls import path, include
from rest_framework.authtoken import views

from rest_framework.routers import DefaultRouter

from tech_api.views import OrderSyncViewSet, TransitSyncViewSet, UserSyncViewSet, ClientSyncViewSet, \
    ContractorSyncViewSet, AuditorSyncViewSet, CounterpartySyncViewSet, FullLogViewSet, GetToken, ContactSyncViewSet, \
    CargoSyncViewSet, ExtOrderSyncViewSet, SegmentSyncViewSet, ClientContractSyncViewSet, \
    ContractorContractSyncViewSet, ExtraServiceViewSet, ExtraCargoParamsViewSet

router = DefaultRouter()
router.register('orders', OrderSyncViewSet, basename='orders')
router.register('transits', TransitSyncViewSet, basename='transits')
router.register('users', UserSyncViewSet, basename='users')
router.register('clients', ClientSyncViewSet, basename='clients')
router.register('contractors', ContractorSyncViewSet, basename='contractors')
router.register('auditors', AuditorSyncViewSet, basename='clients')
router.register('counterparties', CounterpartySyncViewSet, basename='counterparties')
router.register('contacts', ContactSyncViewSet, basename='contacts')
router.register('cargos', CargoSyncViewSet, basename='cargos')
router.register('ext_orders', ExtOrderSyncViewSet, basename='ext_orders')
router.register('segments', SegmentSyncViewSet, basename='segments')
router.register('client_contracts', ClientContractSyncViewSet, basename='client_contracts')
router.register('contractor_contracts', ContractorContractSyncViewSet, basename='contractor_contracts')
router.register('extra_services', ExtraServiceViewSet, basename='extra_services')
router.register('extra_cargo_params', ExtraCargoParamsViewSet, basename='extra_cargo_params')
router.register('log', FullLogViewSet, basename='log')

urlpatterns = [
    path('get_token/', GetToken.as_view()),
    path('', include(router.urls))
]
