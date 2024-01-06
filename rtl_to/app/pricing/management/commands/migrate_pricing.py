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
            if hasattr(order, 'orderprice'):
                order.orderprice.delete()
            price_date = order.to_date_fact if order.to_date_fact else timezone.now().date()
            op = OrderPrice.objects.create(order=order, price_date=price_date)
            if order.type == 'internal':
                for transit in order.transits.all():
                    bp = BillPosition.objects.create(transit=transit, order_price=op, value=transit.price,
                                                     currency=transit.price_currency, taxes=order.taxes,
                                                     bill_number=transit.bill_number)
                    transit.segments.update(bill_position=bp)
                    bp.update_from_segments()
            else:
                for ext_order in order.ext_orders.all():
                    bp = BillPosition.objects.create(transit=ext_order.transit, order_price=op,
                                                     value=ext_order.price_client, currency=ext_order.currency_client,
                                                     taxes=ext_order.taxes, bill_number=ext_order.bill_client)
                    ext_order.segments.update(bill_position=bp)
                    bp.update_from_segments()
            op.update_pricing()
            self.stdout.write('Done')
