from django.core.management.base import BaseCommand

from orders.models import Transit


class Command(BaseCommand):

    def handle(self, *args, **options):
        departure_changes = ('from_addr', 'from_addr_short', 'from_addr_eng', 'sender', 'from_contacts')
        delivery_changes = ('to_addr', 'to_addr_short', 'to_addr_eng', 'receiver', 'to_contacts')
        for transit in Transit.objects.all():
            transit.change_child('ext_orders', 'first', departure_changes)
            transit.change_child('segments', 'first', departure_changes)
            transit.change_child('ext_orders', 'last', delivery_changes)
            transit.change_child('segments', 'last', delivery_changes)
