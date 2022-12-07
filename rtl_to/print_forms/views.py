import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from orders.models import TransitSegment, Transit, ExtOrder
from print_forms.forms import WaybillDataForm, DocOriginalForm, TransDocDataForm, ShippingReceiptOriginalForm
from print_forms.generator import PDFGenerator
from print_forms.models import TransDocsData, DocOriginal, DOC_TYPES, ShippingReceiptOriginal


def segment_docs(request, segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)
    return render(request, 'print_forms/pages/segment_docs.html', {'segment': segment})


class PDFDataAddTpl(View):
    template_name = None
    form_class = None

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        if segment.ext_order.number == segment.order.inner_number:
            delimiter = '-'
        else:
            delimiter = '.'
        waybill_number = f'{segment.ext_order.number}{delimiter}{segment.ext_order.waybills.count() + 1}'
        form = self.form_class(initial={
            'doc_number': waybill_number,
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'quantity': segment.quantity,
            'weight_brut': segment.weight_brut,
            'value': segment.transit.value
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request, segment_pk):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            wd = form.save(False)
            wd.segment = TransitSegment.objects.get(pk=segment_pk)
            wd.save()
            return redirect('segment_docs', segment_pk=str(segment_pk))
        print(form.errors)
        return render(request, self.template_name, {'form': form})


class WaybillPFDataAddView(PDFDataAddTpl):
    template_name = 'print_forms/pages/waybill_add.html'
    form_class = WaybillDataForm


class TransDocAddView(PDFDataAddTpl):
    template_name = 'print_forms/pages/waybill_add.html'
    form_class = TransDocDataForm


class OrigDocumentAddView(View):

    @staticmethod
    def get_types_choices(segment_type):
        if segment_type == 'auto':
            allowed_keys = ['auto', 'cmr']
        else:
            allowed_keys = [segment_type]

        return tuple(filter(lambda x: x[0] in allowed_keys, DOC_TYPES))

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = DocOriginalForm(initial={
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'load_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'quantity': segment.quantity,
            'weight_brut': segment.weight_brut,
            'weight_payed': segment.weight_payed,
        })
        form.fields.get('doc_type').choices = self.get_types_choices(segment.type)
        return render(request, 'print_forms/pages/original_add.html', {'form': form})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = DocOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.save()
            return redirect('segment_docs', segment_pk=segment_pk)
        form.fields.get('doc_type').choices = self.get_types_choices(segment.type)
        return render(request, 'print_forms/pages/original_add.html', {'form': form})


class DocOriginalEdit(UpdateView):
    model = DocOriginal
    form_class = DocOriginalForm
    template_name = 'print_forms/pages/original_edit.html'

    @staticmethod
    def get_types_choices(segment_type):
        if segment_type == 'auto':
            allowed_keys = ['auto', 'cmr']
        else:
            allowed_keys = [segment_type]
        return tuple(filter(lambda x: x[0] in allowed_keys, DOC_TYPES))

    def get_form(self, form_class=None):
        form = super(DocOriginalEdit, self).get_form(form_class)
        form.fields.get('doc_type').choices = self.get_types_choices(form.instance.segment.type)
        return form

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class DocOriginalDelete(DeleteView):
    model = DocOriginal
    template_name = 'print_forms/pages/original_delete.html'

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class ReceiptOriginalAddView(View):

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = ShippingReceiptOriginalForm(initial={
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'load_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
        })
        return render(request, 'print_forms/pages/receipt_original_add.html', {'form': form})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = ShippingReceiptOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.save()
            return redirect('segment_docs', segment_pk=segment_pk)
        return render(request, 'print_forms/pages/receipt_original_add.html', {'form': form})


class ReceiptOriginalEditView(UpdateView):
    model = ShippingReceiptOriginal
    form_class = ShippingReceiptOriginalForm
    template_name = 'print_forms/pages/receipt_original_edit.html'

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class ReceiptOriginalDeleteView(DeleteView):
    model = ShippingReceiptOriginal
    template_name = 'print_forms/pages/receipt_original_delete.html'

    def get_success_url(self):
        return reverse(f'segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class WaybillPFDataEditView(UpdateView):
    model = TransDocsData
    form_class = WaybillDataForm
    template_name = 'print_forms/pages/waybill_edit.html'

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class TransDocPFDataEditView(UpdateView):
    model = TransDocsData
    form_class = TransDocDataForm
    template_name = 'print_forms/pages/waybill_edit.html'

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class WaybillPFDataDeleteView(DeleteView):
    model = TransDocsData
    template_name = 'print_forms/pages/waybill_delete.html'

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


def waybill(request, docdata_pk, filename):
    docdata = TransDocsData.objects.get(pk=docdata_pk)
    context = {
        'waybill_data': docdata,
        'segment': docdata.segment,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in docdata.segment.transit.cargos.all()]))
        ).lower(),
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/waybill.html', context)


def shipping_receipt(request, docdata_pk, filename):
    docdata = TransDocsData.objects.get(pk=docdata_pk)
    context = {
        'docdata': docdata,
        'segment': docdata.segment,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in docdata.segment.transit.cargos.all()]))
        ).lower(),
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/shipping_receipt.html', context)


def cargo_params(transit):
    cargos = transit.cargos.all()
    existing_params = set()
    for cargo in cargos:
        for param in cargo.extra_params.all():
            existing_params.add(str(param))

    result = list()

    if 'Хрупкий' in existing_params:
        result.append('Хрупкий груз')
    else:
        result.append('Не хрупкий груз')

    if 'Опасный' in existing_params:
        result.append('Опасный груз')
    else:
        result.append('Не опасный груз')

    for param in 'Боится влаги', 'Боится деформации':
        if param in existing_params:
            result.append(param)

    return '; '.join(result)


def shipping_receipt_ext(request, transit_pk, filename):
    transit = Transit.objects.get(pk=transit_pk)
    context = {
        'transit': transit,
        'order': transit.order,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in transit.cargos.all()]))
        ).lower(),
        'cargo_params': cargo_params(transit),
        'extra_services': '; '.join([str(i) for i in transit.extra_services.all()]),
        'fax': request.GET.get('fax', False)
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/shipping_receipt_ext.html', context)


def ext_order_blank(request, order_pk, filename):
    ext_order = ExtOrder.objects.get(pk=order_pk)
    doc_types_dict = {i[0]: i[1] for i in DOC_TYPES}
    context = {
        'ext_order': ext_order,
        'packages': ', '.join(
            list(set([cargo.get_package_type_display() for cargo in ext_order.transit.cargos.all()]))
        ).lower(),
        'necessary_docs': ', '.join([doc_types_dict.get(segment.type) for segment in ext_order.segments.all()]),
        'cargo_params': cargo_params(ext_order.transit),
        'extra_services': '; '.join([str(i) for i in ext_order.transit.extra_services.all()]),
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/ext_order_blank.html', context)


def bills_blank(request, filename):
    post_data = request.session.get('bill_data')
    start, end = [datetime.date.fromisoformat(i) for i in request.session.get('period')]
    contexts_list = list()
    for bill_number, trans_ids in post_data.items():
        queryset = Transit.objects.filter(pk__in=trans_ids)
        queryset.update(bill_number=bill_number if bill_number != 'null' else None)
        contexts_list.append({
            'bill_number': bill_number, 'queryset': queryset, 'start': start, 'end': end,
            'sum_price_wo_taxes': round(sum([i.price_wo_taxes() for i in queryset]), 2),
            'sum_taxes_sum': round(sum([i.taxes_sum() for i in queryset if i.taxes_sum()]), 2),
            'sum_price': round(sum([i.price for i in queryset]), 2)
        })
    generator = PDFGenerator(filename)
    return generator.merged_response('print_forms/docs/bill.html', contexts_list)
    # return redirect('bill_output')
