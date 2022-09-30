import string

from django.core.management.base import BaseCommand
import random
from orders.models import Transit, TransitSegment


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Transit.objects.all()

    @staticmethod
    def __random_string(length):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

    def handle(self, *args, **options):
        from_addr = None
        for transit in self.queryset:
            segments = list()
            for i in range(3):
                to_addr = self.__random_string(15)
                segments.append(TransitSegment(
                    from_addr=self.__random_string(15) if from_addr is None else from_addr,
                    to_addr=to_addr,
                    sender=transit.sender,
                    receiver=transit.receiver,
                    type=random.choice(['auto', 'plane']),
                    quantity=transit.quantity,
                    weight_payed=transit.weight,
                    transit=transit
                ))
                from_addr = to_addr
            TransitSegment.objects.bulk_create(segments)
