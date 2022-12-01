from django.core.management.base import BaseCommand

from app_auth.models import Counterparty


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Counterparty.objects.all()
        self.duplicates = dict()
        self.collect_non_unique()

    def collect_non_unique(self):
        for cp in self.queryset:
            label = str(cp)
            if label not in self.duplicates:
                self.duplicates.setdefault(label, list())
            self.duplicates[label].append(cp)
        for label, cp_list in self.duplicates:
            if len(cp_list) <= 1:
                self.duplicates.pop(label)

    def handle(self, *args, **options):
        print(len(self.duplicates))
