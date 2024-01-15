from django.urls import path, include
from rest_framework.authtoken import views

from rest_framework.routers import DefaultRouter

from tech_api.views import OrderSyncViewSet, TransitSyncViewSet, UserSyncViewSet, ClientSyncViewSet, \
    ContractorSyncViewSet, AuditorSyncViewSet, CounterpartySyncViewSet, FullLogViewSet, GetToken

router = DefaultRouter()
router.register('orders', OrderSyncViewSet, basename='orders')
router.register('transits', TransitSyncViewSet, basename='transits')
router.register('users', UserSyncViewSet, basename='users')
router.register('clients', ClientSyncViewSet, basename='clients')
router.register('contractors', ContractorSyncViewSet, basename='contractors')
router.register('auditors', AuditorSyncViewSet, basename='clients')
router.register('counterparties', CounterpartySyncViewSet, basename='counterparties')
# router.register('contacts', ContactViewSet, basename='contacts')
# router.register('cargos', CargoViewSet, basename='cargos')
# router.register('ext_orders', ExtOrderViewSet, basename='ext_orders')
# router.register('segments', SegmentViewSet, basename='segments')
# router.register('orders', TryingReadOnly, basename='orders')
router.register('log', FullLogViewSet, basename='log')

urlpatterns = [
    path('get_token/', GetToken.as_view()),
    path('', include(router.urls))
]
