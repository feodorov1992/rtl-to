from django.urls import path, include
from rest_framework.authtoken import views

from rest_framework.routers import DefaultRouter

from tech_api.views import OrderSyncViewSet, TransitSyncViewSet, UserSyncViewSet, ClientSyncViewSet, \
    ContractorSyncViewSet, AuditorSyncViewSet, CounterpartySyncViewSet, FullLogViewSet, GetToken, ContactSyncViewSet, \
    CargoSyncViewSet, ExtOrderSyncViewSet, SegmentSyncViewSet, ClientContractSyncViewSet, \
    ContractorContractSyncViewSet, ExtraServiceViewSet, ExtraCargoParamsViewSet, DocOriginalSyncViewSet, \
    ShippingReceiptOriginalSyncViewSet, RandomDocScanSyncViewSet, TransDocsDataSyncViewSet, OrderPriceSyncViewSet, \
    BillPositionSyncViewSet

router = DefaultRouter()
router.register('logistics/orders', OrderSyncViewSet, basename='orders')
router.register('logistics/transits', TransitSyncViewSet, basename='transits')
router.register('service/users', UserSyncViewSet, basename='users')
router.register('orgs/clients', ClientSyncViewSet, basename='clients')
router.register('orgs/contractors', ContractorSyncViewSet, basename='contractors')
router.register('orgs/auditors', AuditorSyncViewSet, basename='clients')
router.register('counterparties/counterparties', CounterpartySyncViewSet, basename='counterparties')
router.register('counterparties/contacts', ContactSyncViewSet, basename='contacts')
router.register('logistics/cargos', CargoSyncViewSet, basename='cargos')
router.register('logistics/ext_orders', ExtOrderSyncViewSet, basename='ext_orders')
router.register('logistics/segments', SegmentSyncViewSet, basename='segments')
router.register('contracts/client_contracts', ClientContractSyncViewSet, basename='client_contracts')
router.register('contracts/contractor_contracts', ContractorContractSyncViewSet, basename='contractor_contracts')
router.register('extra/services', ExtraServiceViewSet, basename='extra_services')
router.register('extra/cargo_params', ExtraCargoParamsViewSet, basename='extra_cargo_params')
router.register('docs/trans_scans', DocOriginalSyncViewSet, basename='trans_scans')
router.register('docs/receipt_scans', ShippingReceiptOriginalSyncViewSet, basename='receipt_scans')
router.register('docs/random_scans', RandomDocScanSyncViewSet, basename='random_scans')
router.register('docs/blanks', TransDocsDataSyncViewSet, basename='blanks')
router.register('pricing/order_prices', OrderPriceSyncViewSet, basename='order_prices')
router.register('pricing/bill_positions', BillPositionSyncViewSet, basename='bill_positions')
router.register('service/log', FullLogViewSet, basename='log')

urlpatterns = [
    path('service/get_token/', GetToken.as_view()),
    path('', include(router.urls))
]
