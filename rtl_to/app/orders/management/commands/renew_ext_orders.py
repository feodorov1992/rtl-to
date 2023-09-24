from django.core.management.base import BaseCommand

from orders.models import ExtOrder


class Command(BaseCommand):

    def handle(self, *args, **options):
        for eo in ExtOrder.objects.all():
            eo.weight_payed = eo.equal_to_max(eo.segments.all(), 'weight_payed')
            eo.docs_list_update()
