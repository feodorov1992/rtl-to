from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView

from orders.models import TransitSegment
from print_forms.generator import PDFGenerator
from print_forms.models import WaybillData


class KindaModel:
    OWN_TYPES = (
        ('own', 'Собственность'),
        ('family', 'Совместная собственность супругов'),
        ('rent', 'Аренда'),
        ('leasing', 'Лизинг'),
        ('free', 'Безвозмездное пользование')
    )

    def ownership_num(self):
        print(self.ownership)
        for t, _type in enumerate(self.OWN_TYPES):
            print(_type)
            if _type[0] == self.ownership:
                return str(t + 1)
        return str()

    def short_name(self):
        result = [self.driver_last_name]
        for arg in self.driver_first_name, self.driver_second_name:
            if isinstance(arg, str):
                result.append(f'{arg[0].capitalize()}.')
        return ' '.join(result)


def get_waybill_data(segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)

    waybill_data = KindaModel()

    waybill_data.segment = segment
    waybill_data.waybill_number = f'{segment.ext_order.number}/1'
    waybill_data.driver_last_name = 'Мишагин'
    waybill_data.driver_first_name = 'Михаил'
    waybill_data.driver_second_name = 'Михайлович'
    waybill_data.driver_license = '9921 987491'
    waybill_data.driver_entity = 'РФ'
    waybill_data.auto_model = 'ГАЗЕЛЬ НЕКСТ 3009NA'
    waybill_data.auto_number = 'К 052 СО/73'
    waybill_data.ownership = 'leasing'
    return waybill_data


def auto_docs(request, segment_pk):
    waybills = WaybillData.objects.filter(segment__pk=segment_pk)
    return render(request, '', {'waybills': waybills})


class WaybillDataAddView(CreateView):
    model = WaybillData
    template_name = ''


def aero_docs(request, segment_pk):
    return render(request, '', {})


def waybill_no_name(request, waybill_pk):
    waybill_data = WaybillData.objects.get(pk=waybill_pk)
    filename = waybill_data.waybill_number.replace('/', '_').replace('-', '_') + '.pdf'
    return redirect(reverse('waybill', kwargs={
        'segment_pk': str(waybill_pk),
        'filename': filename
    }))


def waybill(request, segment_pk, filename):

    waybill_data = get_waybill_data(segment_pk)

    context = {
        'waybill_data': waybill_data,
        'segment': waybill_data.segment,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in waybill_data.segment.transit.cargos.all()]))
        ).lower(),
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/waybill.html', context)


def waybill_page(request, segment_pk):
    waybill_data = get_waybill_data(segment_pk)

    waybill_data = get_waybill_data(segment_pk)

    context = {
        'waybill_data': waybill_data,
        'segment': waybill_data.segment,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in waybill_data.segment.transit.cargos.all()]))
        ).lower(),
    }
    # filename = waybill_data.waybill_number.replace('/', '_').replace('-', '_') + '.pdf'
    #
    # generator = PDFGenerator(filename)
    return render(request, 'print_forms/docs/waybill.html', context)
