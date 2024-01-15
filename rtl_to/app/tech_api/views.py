from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app_auth.models import User, Client, Contractor, Auditor, Counterparty, Contact
from orders.models import Order, Transit
from tech_api.models import SyncLogEntry
from tech_api.serializers import OrderSerializer, TransitSerializer, UserSerializer, ClientSerializer, \
    ContractorSerializer, AuditorSerializer, CounterpartySerializer, ContactSerializer, ReportSerializer, \
    FullLogSerializer


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


class ReadOnlySyncViewSet(ReadOnlyModelViewSet):
    report_serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    limit = 500
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]

    def get_queryset(self):
        log_entries = SyncLogEntry.objects.filter(
            node=self.request.user.username, object_type=self.model.__name__
        ).values_list('obj_pk', 'obj_last_update')
        versions_mapper = {pk: last_update.timestamp() for pk, last_update in log_entries}
        obj_ids = list()
        for pk, last_update in self.model.objects.order_by('-last_update').values_list('pk', 'last_update'):
            logged_timestamp = versions_mapper.get(pk)
            if logged_timestamp is None or logged_timestamp < last_update.timestamp():
                obj_ids.append(pk)
                if self.limit is not None and len(obj_ids) == self.limit:
                    break
        return self.model.objects.filter(pk__in=obj_ids)

    def get_object(self):
        return get_object_or_404(self.model, **self.kwargs)

    def get_serializer_class(self):
        if self.action == 'add_report':
            return self.report_serializer_class
        return self.model_serializer_class

    @extend_schema(request=ReportSerializer(many=True))
    @action(detail=False, methods=['post'])
    def add_report(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            node = request.user.username
            object_type = self.model.__name__
            existing_log_entries = SyncLogEntry.objects.filter(
                node=node, object_type=object_type, obj_pk__in=[obj.get('obj_pk') for obj in serializer.data]
            )
            existing_log_entries_count = existing_log_entries.count()
            created_log_entries_count = len(serializer.data) - existing_log_entries_count
            existing_log_entries.delete()
            entries = [
                SyncLogEntry(object_type=object_type, node=node, obj_pk=obj.get('obj_pk'),
                         obj_last_update=obj.get('obj_last_update'))
                for obj in serializer.data
            ]
            SyncLogEntry.objects.bulk_create(entries)
            return Response({
                'node': node, 'object_type': object_type, 'creation_status': 'OK',
                'updated_entries': existing_log_entries_count,
                'created_entries': created_log_entries_count
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Service'])
class GetToken(ObtainAuthToken):
    pass


@extend_schema(tags=['Service'])
class FullLogViewSet(ReadOnlyModelViewSet):
    queryset = SyncLogEntry.objects.all()
    serializer_class = FullLogSerializer

    filter_backends = [
        DjangoFilterBackend
    ]

    filterset_fields = [
        'object_type',
        'node'
    ]


@extend_schema(tags=['Logistics'])
class OrderSyncViewSet(ReadOnlySyncViewSet):
    model = Order
    model_serializer_class = OrderSerializer

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


@extend_schema(tags=['Logistics'])
class TransitSyncViewSet(ReadOnlySyncViewSet):
    model = Transit
    model_serializer_class = TransitSerializer

    filterset_fields = [
        'order',
        'type',
        'status'
    ]

    search_fields = [
        'number'
    ]


@extend_schema(tags=['Service'])
class UserSyncViewSet(ReadOnlySyncViewSet):
    model = User
    model_serializer_class = UserSerializer

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


@extend_schema(tags=['Organisations'])
class ClientSyncViewSet(ReadOnlySyncViewSet):
    model = Client
    model_serializer_class = ClientSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Organisations'])
class ContractorSyncViewSet(ReadOnlySyncViewSet):
    model = Contractor.objects.all()
    model_serializer_class = ContractorSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Organisations'])
class AuditorSyncViewSet(ReadOnlySyncViewSet):
    model = Auditor
    model_serializer_class = AuditorSerializer

    search_fields = [
        'inn',
        'kpp',
        'ogrn',
        'short_name',
        'full_name',
    ]


@extend_schema(tags=['Organisations'])
class CounterpartySyncViewSet(ReadOnlySyncViewSet):
    model = Counterparty
    model_serializer_class = CounterpartySerializer

    filterset_fields = [
        'client',
        'contractor',
        'admin'
    ]


@extend_schema(tags=['Organisations'])
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
