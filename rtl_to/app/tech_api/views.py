import logging
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, BooleanFilter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app_auth.models import User, Client, Contractor, Auditor, Counterparty, Contact, ClientContract, ContractorContract
from orders.models import Order, Transit, Cargo, ExtOrder, TransitSegment, ExtraService, ExtraCargoParams
from pricing.models import OrderPrice, BillPosition
from print_forms.models import DocOriginal, ShippingReceiptOriginal, RandomDocScan, TransDocsData
from tech_api.models import SyncLogEntry
from tech_api.serializers import OrderSerializer, TransitSerializer, UserSerializer, ClientSerializer, \
    ContractorSerializer, AuditorSerializer, CounterpartySerializer, ContactSerializer, ReportSerializer, \
    FullLogSerializer, CargoSerializer, ExtOrderSerializer, SegmentSerializer, ClientContractSerializer, \
    ContractorContractSerializer, ExtraServiceSerializer, ExtraCargoParamsSerializer, DocOriginalSerializer, \
    ShippingReceiptOriginalSerializer, RandomDocScanSerializer, TransDocsDataSerializer, OrderPriceSerializer, \
    BillPositionSerializer, OrderCompiledSerializer

logger = logging.getLogger(__name__)


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


class SyncViewSetV2(ReadOnlyModelViewSet):
    report_serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]

    def get_queryset(self):
        return self.model.objects.all()

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
            logging.error(request.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ReadOnlySyncViewSet(SyncViewSetV2):
    limit = 500

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


class OuterIDSearchMxin:

    @action(methods=['get'], detail=True)
    def outer_retrieve(self, request, *args, **kwargs):
        object_id = self.kwargs.get('pk')
        obj = get_object_or_404(self.model, id_1c=object_id)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class SyncViewSet(CreateModelMixin, UpdateModelMixin, ReadOnlySyncViewSet):
    pass


@extend_schema(tags=['Service'])
class GetToken(ObtainAuthToken):
    pass


@extend_schema(tags=['Service'])
class FullLogViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
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

    filterset_fields = {
        'client': ['exact'],
        'type': ['exact'],
        'manager': ['exact'],
        'status': ['in', 'exact'],
        'order_date': ['lte', 'gte']
    }

    search_fields = [
        'inner_number',
        'client_number'
    ]

    @extend_schema(responses=OrderCompiledSerializer(), filters=None)
    @action(detail=True, methods=['get'], filter_backends=[])
    def compiled(self, request, pk):
        order = self.model.objects.get(pk=pk)
        serializer = OrderCompiledSerializer(order)
        return Response(serializer.data)


class OrdersPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class OrderFilterSet(FilterSet):
    ignore_logs = BooleanFilter(method='filter_ignore_logs')

    @staticmethod
    def get_logs_mapper(node, model):
        log_entries = SyncLogEntry.objects.filter(node=node, object_type=model).values_list('obj_pk', 'obj_last_update')
        return {pk: last_update.timestamp() for pk, last_update in log_entries}

    def logs_compare(self, request, queryset):
        logs_mapper = self.get_logs_mapper(request.user.username, queryset.model.__name__)
        if not logs_mapper:
            return queryset
        free_obj_ids = list()
        for pk, last_update in queryset.order_by('-last_update').values_list('pk', 'last_update'):
            logged_timestamp = logs_mapper.get(pk)
            if logged_timestamp is None or logged_timestamp < last_update.timestamp():
                free_obj_ids.append(pk)
        if not free_obj_ids:
            return queryset.none()
        return queryset.filter(id__in=free_obj_ids)

    def filter_ignore_logs(self, queryset, name, value):
        if value:
            return queryset
        return self.logs_compare(self.request, queryset)

    def filter_queryset(self, queryset):
        if self.form.cleaned_data.get('ignore_logs') is None:
            self.form.cleaned_data['ignore_logs'] = False
        return super(OrderFilterSet, self).filter_queryset(queryset)

    class Meta:
        model = Order
        fields = {
            'client': ['exact'],
            'type': ['exact'],
            'manager': ['exact'],
            'status': ['in', 'exact'],
            'order_date': ['lte', 'gte']
        }


@extend_schema(tags=['V2'])
class OrderSyncViewSetV2(SyncViewSetV2):
    model = Order
    model_serializer_class = OrderSerializer
    pagination_class = OrdersPagination
    filterset_class = OrderFilterSet

    search_fields = [
        'inner_number',
        'client_number'
    ]

    @extend_schema(responses=OrderCompiledSerializer(), filters=None)
    @action(detail=True, methods=['get'], filter_backends=[])
    def compiled(self, request, pk):
        order = self.model.objects.get(pk=pk)
        serializer = OrderCompiledSerializer(order)
        return Response(serializer.data)


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
class ClientSyncViewSet(OuterIDSearchMxin, SyncViewSet):
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
class ContractorSyncViewSet(OuterIDSearchMxin, SyncViewSet):
    model = Contractor
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


@extend_schema(tags=['Counterparties'])
class CounterpartySyncViewSet(ReadOnlySyncViewSet):
    model = Counterparty
    model_serializer_class = CounterpartySerializer

    filterset_fields = [
        'client',
        'contractor',
        'admin'
    ]


@extend_schema(tags=['Counterparties'])
class ContactSyncViewSet(ReadOnlySyncViewSet):
    model = Contact
    model_serializer_class = ContactSerializer

    filterset_fields = [
        'cp'
    ]

    search_fields = [
        'last_name',
        'email'
    ]


@extend_schema(tags=['Logistics'])
class CargoSyncViewSet(ReadOnlySyncViewSet):
    model = Cargo
    model_serializer_class = CargoSerializer

    filterset_fields = [
        'transit'
    ]


@extend_schema(tags=['Logistics'])
class ExtOrderSyncViewSet(ReadOnlySyncViewSet):
    model = ExtOrder
    model_serializer_class = ExtOrderSerializer

    filterset_fields = [
        'order',
        'transit',
    ]


@extend_schema(tags=['Logistics'])
class SegmentSyncViewSet(ReadOnlySyncViewSet):
    model = TransitSegment
    model_serializer_class = SegmentSerializer

    filterset_fields = [
        'order',
        'transit',
        'ext_order'
    ]


@extend_schema(tags=['Contracts'])
class ClientContractSyncViewSet(OuterIDSearchMxin, SyncViewSet):
    model = ClientContract
    model_serializer_class = ClientContractSerializer

    filterset_fields = [
        'client',
        'currency'
    ]

    search_fields = [
        'name',
        'number',
        'add_agreement_number'
    ]


@extend_schema(tags=['Contracts'])
class ContractorContractSyncViewSet(OuterIDSearchMxin, SyncViewSet):
    model = ContractorContract
    model_serializer_class = ContractorContractSerializer

    filterset_fields = [
        'contractor',
        'currency'
    ]

    search_fields = [
        'name',
        'number',
        'add_agreement_number'
    ]


@extend_schema(tags=['Extra Params'])
class ExtraServiceViewSet(ReadOnlyModelViewSet):
    queryset = ExtraService.objects.all()
    serializer_class = ExtraServiceSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Extra Params'])
class ExtraCargoParamsViewSet(ReadOnlyModelViewSet):
    queryset = ExtraCargoParams.objects.all()
    serializer_class = ExtraCargoParamsSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Docs'])
class DocOriginalSyncViewSet(ReadOnlySyncViewSet):
    model = DocOriginal
    model_serializer_class = DocOriginalSerializer

    filterset_fields = [
        'segment',
        'transit'
    ]

    search_fields = [
        'doc_number'
    ]


@extend_schema(tags=['Docs'])
class ShippingReceiptOriginalSyncViewSet(ReadOnlySyncViewSet):
    model = ShippingReceiptOriginal
    model_serializer_class = ShippingReceiptOriginalSerializer

    filterset_fields = [
        'segment',
        'transit'
    ]

    search_fields = [
        'doc_number'
    ]


@extend_schema(tags=['Docs'])
class RandomDocScanSyncViewSet(ReadOnlySyncViewSet):
    model = RandomDocScan
    model_serializer_class = RandomDocScanSerializer

    filterset_fields = [
        'segment',
        'transit'
    ]

    search_fields = [
        'doc_number'
    ]


@extend_schema(tags=['Docs'])
class TransDocsDataSyncViewSet(ReadOnlySyncViewSet):
    model = TransDocsData
    model_serializer_class = TransDocsDataSerializer

    filterset_fields = [
        'segment',
        'ext_order'
    ]

    search_fields = [
        'doc_number',
        'doc_num_trans'
    ]


@extend_schema(tags=['Pricing'])
class OrderPriceSyncViewSet(ReadOnlySyncViewSet):
    model = OrderPrice
    model_serializer_class = OrderPriceSerializer

    filterset_fields = [
        'order'
    ]


@extend_schema(tags=['Pricing'])
class BillPositionSyncViewSet(ReadOnlySyncViewSet):
    model = BillPosition
    model_serializer_class = BillPositionSerializer

    filterset_fields = [
        'order_price',
        'transit',
        'bill_number'
    ]
