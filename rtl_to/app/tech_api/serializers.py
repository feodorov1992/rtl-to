from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from app_auth.models import User, Client, Contractor, Auditor, Counterparty, Contact, ClientContract, ContractorContract
from orders.models import Order, Transit, Cargo, ExtOrder, TransitSegment, ExtraService, ExtraCargoParams
from pricing.models import OrderPrice, BillPosition
from print_forms.models import DocOriginal, ShippingReceiptOriginal, RandomDocScan, TransDocsData
from tech_api.models import SyncLogEntry


class OrderSerializer(ModelSerializer):
    orderprice = PrimaryKeyRelatedField(read_only=True, label='Ставка')

    class Meta:
        model = Order
        exclude = 'from_addr_forlist', 'to_addr_forlist', 'active_segments', 'price'


class TransitSerializer(ModelSerializer):

    class Meta:
        model = Transit
        exclude = ('api_id', 'from_org', 'from_inn', 'from_legal_addr', 'from_contact_name', 'from_contact_phone',
                   'from_contact_email', 'to_org', 'to_inn', 'to_legal_addr', 'to_contact_name', 'to_contact_phone',
                   'to_contact_email', 'price', 'price_currency', 'price_from_eo', 'bill_number')


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined', 'boss', 'groups', 'user_permissions', 'is_staff',
                   'is_active', 'is_superuser')


class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        exclude = 'num_prefix', 'order_label', 'order_template', 'receipt_template'


class ContractorSerializer(ModelSerializer):

    class Meta:
        model = Contractor
        exclude = 'order_label', 'order_template', 'receipt_template'


class AuditorSerializer(ModelSerializer):

    class Meta:
        model = Auditor
        fields = '__all__'


class CounterpartySerializer(ModelSerializer):

    class Meta:
        model = Counterparty
        fields = '__all__'


class ContactSerializer(ModelSerializer):

    class Meta:
        model = Contact
        fields = '__all__'


class ReportSerializer(ModelSerializer):

    class Meta:
        model = SyncLogEntry
        fields = 'obj_pk', 'obj_last_update'


class FullLogSerializer(ModelSerializer):

    class Meta:
        model = SyncLogEntry
        fields = '__all__'


class CargoSerializer(ModelSerializer):

    class Meta:
        model = Cargo
        fields = '__all__'


class ExtOrderSerializer(ModelSerializer):

    class Meta:
        model = ExtOrder
        exclude = 'price_client', 'currency_client', 'bill_client', 'docs_list'


class SegmentSerializer(ModelSerializer):
    class Meta:
        model = TransitSegment
        exclude = ('ordering_num', 'api_id', 'price', 'price_carrier', 'taxes', 'currency', 'contract',
                   'tracking_number', 'tracking_date')


class ClientContractSerializer(ModelSerializer):

    class Meta:
        model = ClientContract
        exclude = 'order_label', 'order_template', 'receipt_template'


class ContractorContractSerializer(ModelSerializer):
    class Meta:
        model = ContractorContract
        exclude = 'order_label', 'order_template', 'receipt_template'


class ExtraServiceSerializer(ModelSerializer):

    class Meta:
        model = ExtraService
        fields = '__all__'


class ExtraCargoParamsSerializer(ModelSerializer):

    class Meta:
        model = ExtraCargoParams
        fields = '__all__'


class DocOriginalSerializer(ModelSerializer):

    class Meta:
        model = DocOriginal
        fields = '__all__'


class ShippingReceiptOriginalSerializer(ModelSerializer):

    class Meta:
        model = ShippingReceiptOriginal
        fields = '__all__'


class RandomDocScanSerializer(ModelSerializer):
    class Meta:
        model = RandomDocScan
        fields = '__all__'


class TransDocsDataSerializer(ModelSerializer):
    class Meta:
        model = TransDocsData
        fields = '__all__'


class OrderPriceSerializer(ModelSerializer):

    class Meta:
        model = OrderPrice
        fields = '__all__'


class BillPositionSerializer(ModelSerializer):

    class Meta:
        model = BillPosition
        fields = '__all__'


class CargoCompiledSerializer(ModelSerializer):
    class Meta:
        model = Cargo
        exclude = 'transit',


class TransitCompiledSerializer(ModelSerializer):
    full_list = CargoCompiledSerializer(many=True, read_only=True, source='cargos')

    class Meta:
        model = Transit
        fields = 'volume', 'weight', 'weight_fact', 'quantity', 'quantity_fact', 'value', 'currency', 'full_list'


class BillPositionCompiledSerializer(ModelSerializer):
    cargo = TransitCompiledSerializer(read_only=True, source='transit')

    class Meta:
        model = BillPosition
        exclude = 'order_price', 'transit'


class OrderPriceCompiledSerializer(ModelSerializer):
    positions = BillPositionCompiledSerializer(many=True, read_only=True)

    class Meta:
        model = OrderPrice
        exclude = 'order',


class ContactCompiledSerializer(ModelSerializer):
    class Meta:
        model = Contact
        exclude = 'cp',


class CounterpartyCompiledSerializer(ModelSerializer):

    class Meta:
        model = Counterparty
        exclude = 'admin', 'client', 'contractor'


class ContractorContractCompiledSerializer(ModelSerializer):

    class Meta:
        model = ClientContract
        exclude = 'client', 'order_label', 'order_template', 'receipt_template'


class UserCompiledSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined', 'boss', 'groups', 'user_permissions', 'is_staff',
                   'is_active', 'is_superuser', 'user_type', 'client', 'auditor', 'contractor')


class ExtOrderCompiledSerializer(ModelSerializer):
    from_contacts = ContactCompiledSerializer(many=True, read_only=True)
    to_contacts = ContactCompiledSerializer(many=True, read_only=True)
    contractor = ContractorSerializer(read_only=True)
    contract = ContractorContractCompiledSerializer(read_only=True)
    sender = CounterpartyCompiledSerializer(read_only=True)
    receiver = CounterpartyCompiledSerializer(read_only=True)
    manager = UserCompiledSerializer(read_only=True)
    contractor_employee = UserCompiledSerializer(read_only=True)

    class Meta:
        model = ExtOrder
        exclude = 'price_client', 'currency_client', 'bill_client', 'docs_list', 'order', 'transit'


class ClientContractCompiledSerializer(ModelSerializer):

    class Meta:
        model = ClientContract
        exclude = 'client', 'order_label', 'order_template', 'receipt_template'


class OrderCompiledSerializer(ModelSerializer):
    client = ClientSerializer(read_only=True)
    contract = ClientContractCompiledSerializer(read_only=True)
    ext_orders = ExtOrderCompiledSerializer(many=True, read_only=True)
    price_obj = OrderPriceCompiledSerializer(read_only=True, source='orderprice')
    created_by = UserCompiledSerializer(read_only=True)
    manager = UserCompiledSerializer(read_only=True)
    client_employee = UserCompiledSerializer(read_only=True)

    class Meta:
        model = Order
        exclude = 'from_addr_forlist', 'to_addr_forlist', 'active_segments', 'price', 'auditors'
