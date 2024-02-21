from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order
from pricing.models import OrderPrice, BillPosition


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("order_numbers", nargs="*", type=str)
        parser.add_argument("--exclude", nargs="+", type=str)

    def handle(self, *args, **options):
        order_numbers = options.get('order_numbers')
        exclude = options.get('exclude')

        if order_numbers:
            orders = Order.objects.filter(inner_number__in=order_numbers)
        else:
            orders = Order.objects.all()

        if exclude:
            orders = orders.exclude(inner_number__in=exclude)

        for order in orders:
            self.stdout.write(f'Processing {order}.....', ending='')
            order.copy_prices_as_object()
            self.stdout.write('Done')
