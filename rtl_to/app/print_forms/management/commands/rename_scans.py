from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models
from orders.models import Transit


class Command(BaseCommand):
    RELATED_NAMES = {
        'originals': ('transit', 'doc_type', 'doc_number'),
        'randoms': ('transit', 'doc_name', 'doc_number')
    }

    @staticmethod
    def join_fields(obj: models.Model, filed_names: tuple):
        result = list()
        for filed_name in filed_names:
            result.append(str(obj.__getattribute__(filed_name)))
        return ' '.join(result)

    @staticmethod
    def check_suffix(suffix: str):
        return suffix and all([i.isnumeric() for i in suffix.split('.')])

    def add_suffix(self, number: str, suffix: int):
        if '-' in number:
            maybe_suffix = number.split('-')[-1]
            if self.check_suffix(maybe_suffix):
                number = '-'.join(number.split('-')[:-1])
                maybe_suffix = maybe_suffix.split('.')
                maybe_suffix.append(str(suffix))
                suffix = '.'.join(maybe_suffix)
        return f'{number}-{suffix}'

    def update_field(self, obj, field_name, suffix):
        number = obj.__getattribute__(field_name)
        setattr(obj, field_name, self.add_suffix(number, suffix))
        obj.save()

    def group_docs(self, queryset, field_names):
        result = dict()
        for obj in queryset:
            unique = self.join_fields(obj, field_names)
            if unique not in result:
                result[unique] = list()
            result[unique].append(obj)
        return result

    @staticmethod
    def get_sub_queryset(obj, rel_name):
        return obj.__getattribute__(rel_name).all()

    def handle(self, *args, **options):
        for transit in Transit.objects.all():
            print(transit)
            for rel_name, unique_together in self.RELATED_NAMES.items():
                queryset = self.get_sub_queryset(transit, rel_name)
                grouped_qs = self.group_docs(queryset, unique_together)
                for group in grouped_qs.values():
                    if len(group) > 1:
                        for t, obj in enumerate(group):
                            self.update_field(obj, unique_together[-1], t + 1)

