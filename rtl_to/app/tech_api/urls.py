from django.urls import path, include

from rest_framework.routers import DefaultRouter

from tech_api.views import OrderViewSet, TransitViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('transits', TransitViewSet, basename='transits')
# router.register('cargos', CargoViewSet, basename='cargos')
# router.register('ext_orders', ExtOrderViewSet, basename='ext_orders')
# router.register('segments', SegmentViewSet, basename='segments')

urlpatterns = [
    path('', include(router.urls))
]
