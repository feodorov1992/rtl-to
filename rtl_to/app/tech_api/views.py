from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app_auth.models import User, Client, Contractor, Auditor, Counterparty, Contact
from orders.models import Order, Transit
from tech_api.serializers import OrderSerializer, TransitSerializer, UserSerializer, ClientSerializer, \
    ContractorSerializer, AuditorSerializer, CounterpartySerializer, ContactSerializer


class BackendsMixin:
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]


class ViewSetTemplate(BackendsMixin, ModelViewSet):
    pass


class ReadOnlyViewSetTemplate(BackendsMixin, ReadOnlyModelViewSet):
    pass


@extend_schema(tags=['Поручения (Order)'])
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


@extend_schema(tags=['Перевозки (Transit)'])
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


@extend_schema(tags=['Пользователи (User)'])
class UserViewSet(ViewSetTemplate):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    filterset_fields = {
        'client': ['exact'],
        'auditor': ['exact'],
        'contractor': ['exact'],
        'user_type': ['in', 'exact'],
    }

    search_fields = [
        'last_name',
        'email',
        'username'
    ]


@extend_schema(tags=['Заказчики (Client)'])
class ClientViewSet(ViewSetTemplate):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Перевозчики (Contractor)'])
class ContractorViewSet(ViewSetTemplate):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Аудиторы (Auditor)'])
class AuditorViewSet(ViewSetTemplate):
    queryset = Auditor.objects.all()
    serializer_class = AuditorSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Контрагенты (Counterparty)'])
class CounterpartyViewSet(ViewSetTemplate):
    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer

    filterset_fields = [
        'client',
        'contractor',
        'admin'
    ]


@extend_schema(tags=['Контактные лица (Contact)'])
class ContactViewSet(ViewSetTemplate):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    filterset_fields = [
        'cp'
    ]

    search_fields = [
        'last_name',
        'email'
    ]
