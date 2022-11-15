from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from orders.models import TransitSegment
from print_forms.forms import WaybillDataForm, DocOriginalForm
from print_forms.generator import PDFGenerator
from print_forms.models import WaybillData, DocOriginal


def auto_docs(request, segment):
    scans_wo_waybills = segment.originals.filter(waybill__isnull=True)
    return render(request, 'print_forms/pages/auto_docs.html',
                  {'segment': segment, 'scans_wo_waybills': scans_wo_waybills})


def segment_docs(request, segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)
    if segment.type == 'auto':
        return auto_docs(request, segment)
    return render(request, 'print_forms/pages/segment_docs.html', {'segment': segment})


class WaybillPFDataAddView(View):

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        if segment.ext_order.number == segment.order.inner_number:
            delimiter = '-'
        else:
            delimiter = '.'
        waybill_number = f'{segment.ext_order.number}{delimiter}{segment.ext_order.waybills.count() + 1}'
        form = WaybillDataForm(initial={
            'waybill_number': waybill_number,
            'waybill_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'weight_brut': segment.weight_brut,
        })
        return render(request, 'print_forms/pages/waybill_add.html', {'form': form})

    def post(self, request, segment_pk):
        form = WaybillDataForm(data=request.POST)
        if form.is_valid():
            wd = form.save(False)
            wd.segment = TransitSegment.objects.get(pk=segment_pk)
            wd.save()
            return redirect('segment_docs', segment_pk=str(segment_pk))
        return render(request, 'print_forms/pages/waybill_add.html', {'form': form})


class OrigDocumentAddView(View):

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = DocOriginalForm(initial={
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'load_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'quantity': segment.quantity,
            'weight_brut': segment.weight_brut,
            'weight_payed': segment.weight_payed,
        })
        return render(request, 'print_forms/pages/original_add.html', {'form': form})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = DocOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.doc_type = segment.type
            orig.save()
            return redirect('segment_docs', segment_pk=segment_pk)
        return render(request, 'print_forms/pages/original_add.html', {'form': form})


class WaybillPFDataEditView(UpdateView):
    model = WaybillData
    form_class = WaybillDataForm
    template_name = 'print_forms/pages/waybill_edit.html'

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class WaybillPFDataDeleteView(DeleteView):
    model = WaybillData
    template_name = 'print_forms/pages/waybill_delete.html'

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class WaybillOriginalAddView(View):

    def get(self, request, waybill_pk):
        wd = WaybillData.objects.get(pk=waybill_pk)
        form = DocOriginalForm(initial={
            'doc_number': wd.waybill_number,
            'doc_date': wd.waybill_date,
            'quantity': wd.segment.quantity,
            'weight_payed': wd.weight_brut,
            'weight_brut': wd.weight_brut,
            'load_date': wd.segment.from_date_fact if wd.segment.from_date_fact else wd.segment.from_date_plan
        })
        return render(request, 'print_forms/pages/original_add.html', {'form': form})

    def post(self, request, waybill_pk):
        wd = WaybillData.objects.get(pk=waybill_pk)
        form = DocOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = wd.segment
            orig.transit = wd.segment.transit
            orig.doc_type = 'auto'
            orig.save()
            wd.original = orig
            wd.save()
            return redirect('segment_docs', segment_pk=wd.segment.pk)
        return render(request, 'print_forms/pages/original_add.html', {'form': form})


class DocOriginalEdit(UpdateView):
    model = DocOriginal
    form_class = DocOriginalForm
    template_name = 'print_forms/pages/original_edit.html'

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class DocOriginalDelete(DeleteView):
    model = DocOriginal
    template_name = 'print_forms/pages/original_delete.html'

    def get_context_data(self, **kwargs):
        context = super(DocOriginalDelete, self).get_context_data(**kwargs)
        print(context)
        return context

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


def waybill(request, waybill_pk, filename):
    waybill_data = WaybillData.objects.get(pk=waybill_pk)
    context = {
        'waybill_data': waybill_data,
        'segment': waybill_data.segment,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in waybill_data.segment.transit.cargos.all()]))
        ).lower(),
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/waybill.html', context)
