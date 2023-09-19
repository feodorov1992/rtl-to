from django.core.management.base import BaseCommand

from orders.models import Order, Transit


class Command(BaseCommand):

    def handle(self, *args, **options):
        for transit in Transit.objects.all():
            if transit.price_non_rub and not transit.price:
                transit.price = transit.price_non_rub
                transit.price_non_rub = 0.0
                transit.save()
            elif transit.price and not transit.price_non_rub:
                transit.price_currency = 'RUB'
            elif transit.price_non_rub and transit.price:
                print(transit)

        for order in Order.objects.all():
            order.price = order.get_prices()
            order.save()
