from django.urls import path, include

from rest_framework.routers import DefaultRouter

from tech_api.views import OrderViewSet, TransitViewSet, UserViewSet, ClientViewSet, ContractorViewSet, AuditorViewSet, \
    CounterpartyViewSet, ContactViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('transits', TransitViewSet, basename='transits')
router.register('users', UserViewSet, basename='users')
router.register('clients', ClientViewSet, basename='clients')
router.register('contractors', ContractorViewSet, basename='contractors')
router.register('auditors', AuditorViewSet, basename='clients')
router.register('counterparties', CounterpartyViewSet, basename='counterparties')
router.register('contacts', ContactViewSet, basename='contacts')
# router.register('cargos', CargoViewSet, basename='cargos')
# router.register('ext_orders', ExtOrderViewSet, basename='ext_orders')
# router.register('segments', SegmentViewSet, basename='segments')

urlpatterns = [
    path('', include(router.urls))
]
