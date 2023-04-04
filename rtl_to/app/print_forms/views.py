import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from orders.models import TransitSegment, Transit, ExtOrder
from print_forms.forms import WaybillDataForm, DocOriginalForm, TransDocDataForm, ShippingReceiptOriginalForm
from print_forms.generator import PDFGenerator
from print_forms.models import TransDocsData, DocOriginal, DOC_TYPES, ShippingReceiptOriginal
from print_forms.num2text import Num2Text


def segment_docs(request, segment_pk):
    """
    Страница с перечнем докуменов по плечу (предположительно, не используется)
    """
    segment = TransitSegment.objects.get(pk=segment_pk)
    return render(request, 'print_forms/pages/segment_docs.html', {'segment': segment})


def return_url(user, segment):
    """
    Генератор адреса кнопки "назад"
    """
    if user.user_type == 'manager':
        return reverse('order_detail', kwargs={'pk': segment.order.pk})
    return reverse('order_detail_carrier', kwargs={'pk': segment.ext_order.pk})


class PDFDataAddTpl(View):
    """
    Базовый класс страницы для добавления данных по транспортному средству (для формирования шаблонов ТН/ЭР)
    """
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

        return render(request, self.template_name, {'form': form, 'return_url': return_url(request.user, segment)})

    def post(self, request, segment_pk):
        form = self.form_class(data=request.POST)
        segment = TransitSegment.objects.get(pk=segment_pk)
        if form.is_valid():
            wd = form.save(False)
            wd.segment = segment
            wd.save()
            return redirect(return_url(request.user, segment))
        return render(request, self.template_name, {'form': form, 'return_url': return_url(request.user, segment)})


class WaybillPFDataAddView(PDFDataAddTpl):
    """
    Страница добавления данных по автоперевозке
    """
    template_name = 'print_forms/pages/waybill_add.html'
    form_class = WaybillDataForm


class TransDocAddView(PDFDataAddTpl):
    """
    Страница добавления данных по не-автоперевозке
    """
    template_name = 'print_forms/pages/waybill_add.html'
    form_class = TransDocDataForm


class OrigDocumentAddView(View):
    """
    Страница занесения скана транспортного документа
    """
    @staticmethod
    def get_types_choices(segment_type):
        """
        Генератор перечня типов транспортного документа
        """
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
        return render(request, 'print_forms/pages/original_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = DocOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.save()
            return redirect(return_url(request.user, segment))
        form.fields.get('doc_type').choices = self.get_types_choices(segment.type)
        return render(request, 'print_forms/pages/original_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})


class DocOriginalEdit(UpdateView):
    """
    Страница изменения данных из скана транспортного документа
    """
    model = DocOriginal
    form_class = DocOriginalForm
    template_name = 'print_forms/pages/original_edit.html'

    @staticmethod
    def get_types_choices(segment_type):
        """
        Генератор перечня типов транспортного документа
        """
        if segment_type == 'auto':
            allowed_keys = ['auto', 'cmr']
        else:
            allowed_keys = [segment_type]
        return tuple(filter(lambda x: x[0] in allowed_keys, DOC_TYPES))

    def get_form(self, form_class=None):
        form = super(DocOriginalEdit, self).get_form(form_class)
        form.fields.get('doc_type').choices = self.get_types_choices(form.instance.segment.type)
        return form

    def get_context_data(self, **kwargs):
        context = super(DocOriginalEdit, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return return_url(self.request.user, self.object.segment)


class DocOriginalDelete(DeleteView):
    """
    Страница удаления скана транспортного документа
    """
    model = DocOriginal
    template_name = 'print_forms/pages/original_delete.html'

    def get_context_data(self, **kwargs):
        context = super(DocOriginalDelete, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return return_url(self.request.user, self.object.segment)


class ReceiptOriginalAddView(View):
    """
    Страница добавления скана ЭР
    """

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = ShippingReceiptOriginalForm(initial={
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'load_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
        })
        return render(request, 'print_forms/pages/receipt_original_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = ShippingReceiptOriginalForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.save()
            return redirect(return_url(request.user, segment))
        return render(request, 'print_forms/pages/receipt_original_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})


class ReceiptOriginalEditView(UpdateView):
    """
    Страница изменения скана ЭР
    """
    model = ShippingReceiptOriginal
    form_class = ShippingReceiptOriginalForm
    template_name = 'print_forms/pages/receipt_original_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ReceiptOriginalEditView, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return return_url(self.request.user, self.object.segment)


class ReceiptOriginalDeleteView(DeleteView):
    """
    Страница удаления скана ЭР
    """
    model = ShippingReceiptOriginal
    template_name = 'print_forms/pages/receipt_original_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ReceiptOriginalDeleteView, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return return_url(self.request.user, self.object.segment)


class WaybillPFDataEditView(UpdateView):
    """
    Страница изменения данных по автоперевозке
    """

    model = TransDocsData
    form_class = WaybillDataForm
    template_name = 'print_forms/pages/waybill_edit.html'

    def get_context_data(self, **kwargs):
        context = super(WaybillPFDataEditView, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class TransDocPFDataEditView(UpdateView):
    """
    Страница изменения данных по не-автоперевозке
    """
    model = TransDocsData
    form_class = TransDocDataForm
    template_name = 'print_forms/pages/waybill_edit.html'

    def get_context_data(self, **kwargs):
        context = super(TransDocPFDataEditView, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


class WaybillPFDataDeleteView(DeleteView):
    """
    Страница удаления данных по авто- и не-автоперевозке
    """
    model = TransDocsData
    template_name = 'print_forms/pages/waybill_delete.html'

    def get_context_data(self, **kwargs):
        context = super(WaybillPFDataDeleteView, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return reverse('segment_docs', kwargs={'segment_pk': self.object.segment.pk})


def waybill(request, docdata_pk, filename):
    """
    Печатная форма ТН
    """
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
    """
    Печатная форма ЭР
    """
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
    """
    Коллектор перечня параметров груза для ТН/ЭР
    """
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
    """
    Печатная форма ЭР для заказчика
    """
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
    """
    Печатная форма исходящего ПЭ
    """
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


def get_accounts_context(order_pk):
    """
    Сбор данных для формирования счета и акта
    """
    ext_order = ExtOrder.objects.get(pk=order_pk)
    origs = DocOriginal.objects.filter(segment_id__in=[i.pk for i in ext_order.segments.all()])
    return {
        'ext_order': ext_order,
        'origs': origs,
        'sum_text': Num2Text(ext_order.price_carrier).spell()
    }


def contractor_act_blank(request, order_pk, filename):
    """
    Печатная форма акта
    """
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/contractor_act_blank.html', get_accounts_context(order_pk))


def contractor_bill_blank(request, order_pk, filename):
    """
    Печатная форма счета
    """
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/contractor_bill_blank.html', get_accounts_context(order_pk))


def bills_blank(request, filename):
    """
    Печатная форма детализации для Ротина
    """
    post_data = request.session.get('bill_data')
    if post_data is None:
        return redirect('bill_output')
    start, end = [datetime.date.fromisoformat(i) for i in request.session.get('period')]
    contexts_list = list()
    for bill_number, trans_ids in post_data.items():
        queryset = Transit.objects.filter(pk__in=trans_ids)
        queryset.update(bill_number=bill_number if bill_number != 'null' else None)
        contexts_list.append({
            'bill_number': bill_number, 'queryset': queryset, 'start': start, 'end': end,
            'sum_price_wo_taxes': round(sum([i.price_wo_taxes() for i in queryset if i.price]), 2),
            'sum_taxes_sum': round(sum([i.taxes_sum() for i in queryset if not isinstance(i.taxes_sum(), str)]), 2),
            'sum_price': round(sum([i.price for i in queryset if i.price]), 2)
        })
    generator = PDFGenerator(filename)
    return generator.merged_response('print_forms/docs/bill.html', contexts_list)
