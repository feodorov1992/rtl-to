from django.core.management.base import BaseCommand

from app_auth.models import Counterparty, Client, Contractor


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Counterparty.objects.all()

    @staticmethod
    def collect_non_unique(owner_pk, owner_class):
        result = dict()
        owner = owner_class.objects.get(pk=owner_pk)
        queryset = owner.counterparties.all()
        for cp in queryset:
            label = str(cp)
            if label not in result:
                result.setdefault(label, list())
            result[label].append(cp)
        for label, cp_list in result.copy().items():
            if len(cp_list) <= 1:
                result.pop(label)
        return result

    @staticmethod
    def collect_field(field_name, obj_list):
        for obj in obj_list:
            if hasattr(obj, field_name):
                value = obj.__getattribute__(field_name)
                if value:
                    return value
        else:
            for obj in obj_list:
                if hasattr(obj, field_name):
                    return obj.__getattribute__(field_name)

    def collect_requisites(self, obj_list: list, fields_list: list = None):
        if fields_list is None:
            fields_list = [
                'inn', 'kpp', 'ogrn', 'short_name', 'full_name', 'legal_address', 'fact_address', 'client',
                'contractor', 'admin'
            ]
        kwargs = dict()
        for field in fields_list:
            kwargs[field] = self.collect_field(field, obj_list)
        return kwargs

    @staticmethod
    def merged_contacts(cps_list):
        contacts_list = list()
        for cp in cps_list:
            for contact in cp.contacts.all():
                if contact not in contacts_list:
                    contacts_list.append(contact)
        return contacts_list

    def update_orders(self, cps_list: list):
        new_cp = Counterparty.objects.create(**self.collect_requisites(cps_list))
        new_cp.contacts.add(*self.merged_contacts(cps_list))
        for cp in cps_list:
            for rel_name in 'sent_transits', 'sent_ext_orders', 'sent_segments':
                cp.__getattribute__(rel_name).all().update(sender=new_cp)
            for rel_name in 'received_transits', 'received_ext_orders', 'received_segments':
                cp.__getattribute__(rel_name).all().update(receiver=new_cp)

    def handle(self, *args, **options):
        for client in Client.objects.all():
            non_unique = self.collect_non_unique(client.pk, Client)
            if non_unique:
                for _, obj_list in non_unique.items():
                    self.update_orders(obj_list)
                    for obj in obj_list:
                        obj.delete()
        print()
        for contr in Contractor.objects.all():
            non_unique = self.collect_non_unique(contr.pk, Contractor)
            if non_unique:
                for _, obj_list in non_unique.items():
                    self.update_orders(obj_list)
                    for obj in obj_list:
                        obj.delete()

