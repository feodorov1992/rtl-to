from rest_framework.serializers import ModelSerializer

from orders.models import Order, Transit


class OrderSerializer(ModelSerializer):

    class Meta:
        model = Order
        exclude = 'from_addr_forlist', 'to_addr_forlist', 'active_segments'


class TransitSerializer(ModelSerializer):

    class Meta:
        model = Transit
        exclude = ('api_id', 'from_org', 'from_inn', 'from_legal_addr', 'from_contact_name', 'from_contact_phone',
                   'from_contact_email', 'to_org', 'to_inn', 'to_legal_addr', 'to_contact_name', 'to_contact_phone',
                   'to_contact_email', 'price', 'price_currency', 'price_from_eo', 'bill_number')
