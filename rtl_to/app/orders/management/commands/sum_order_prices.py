from django.core.management.base import BaseCommand

from orders.models import Order, Transit


class Command(BaseCommand):

    def handle(self, *args, **options):
        for transit in Transit.objects.all():
            if transit.price_currency != 'RUB' and not transit.price_non_rub and transit.price:
                transit.price_non_rub = transit.price
                transit.price = 0.0
                transit.save()
            Transit.objects.filter(price_currency='RUB').update(price_currency='USD')

        for order in Order.objects.all():
            order.price = order.get_prices()
            order.save()
