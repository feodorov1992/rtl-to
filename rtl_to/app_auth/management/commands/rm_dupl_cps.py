from django.core.management.base import BaseCommand

from app_auth.models import Counterparty, Client, Contractor


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Counterparty.objects.all()

    @staticmethod
    def collect_non_unique(owner_pk, owner_class):
        result = dict()
        queryset = owner_class.objects.get(owner_pk)
        for cp in queryset:
            label = str(cp)
            if label not in result:
                result.setdefault(label, list())
            result[label].append(cp)
        for label, cp_list in result.copy().items():
            if len(cp_list) <= 1:
                result.pop(label)
        return result

    def handle(self, *args, **options):
        for client in Client.objects.all():
            print(client, len(self.collect_non_unique(client.pk, Client)))
        print()
        for contr in Contractor.objects.all():
            print(contr, len(self.collect_non_unique(contr.pk, Contractor)))

