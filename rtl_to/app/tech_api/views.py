from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from orders.models import Order, Transit
from tech_api.serializers import OrderSerializer, TransitSerializer


class ViewSetTemplate(ModelViewSet):
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]


@extend_schema(tags=['1. Поручения (Order)'])
class OrderViewSet(ViewSetTemplate):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    filterset_fields = [
        'client',
        'type',
        'manager',
        'status'
    ]

    search_fields = [
        'inner_number',
        'client_number'
    ]


@extend_schema(tags=['2. Перевозки (Transit)'])
class TransitViewSet(ViewSetTemplate):
    queryset = Transit.objects.all()
    serializer_class = TransitSerializer

    filterset_fields = [
        'order',
        'type',
        'status'
    ]

    search_fields = [
        'number'
    ]
