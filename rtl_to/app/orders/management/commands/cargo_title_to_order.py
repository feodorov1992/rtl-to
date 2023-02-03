from django.core.management.base import BaseCommand

from orders.models import Order


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Order.objects.all()

    def handle(self, *args, **options):
        for order in self.queryset:
            if not order.cargo_name:
                cargos = list()
                for transit in order.transits.all():
                    for cargo in transit.cargos.all():
                        cargos.append(cargo)
                cargo_titles = list(set([cargo.title for cargo in cargos if cargo.title is not None]))
                order.cargo_name = ', '.join(cargo_titles)
                order.cargo_name = ' '.join(order.cargo_name.split())
                if len(order.cargo_name) > 150:
                    order.cargo_name = order.cargo_name[:150]
                order.save()
