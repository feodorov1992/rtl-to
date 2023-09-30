import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from orders.models import TransitSegment, Transit, ExtOrder, Order, Cargo
from print_forms.forms import WaybillDataForm, DocOriginalForm, TransDocDataForm, ShippingReceiptOriginalForm, \
    RandomDocScanForm
from print_forms.generator import PDFGenerator
from print_forms.models import TransDocsData, DocOriginal, DOC_TYPES, ShippingReceiptOriginal, RandomDocScan
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

    @staticmethod
    def previous_suffix(ext_order, delimiter):
        waybill_numbers = ext_order.waybills.filter(
            doc_number__icontains=ext_order.number
        ).values_list('doc_number', flat=True)
        waybill_suffixes = [i.split(delimiter)[-1] for i in waybill_numbers]
        waybill_suffixes = [int(i) for i in waybill_suffixes if i.isnumeric()]
        if waybill_suffixes:
            return max(waybill_suffixes)
        return ext_order.waybills.count()

    def waybill_number(self, segment):
        if segment.ext_order.number == segment.order.inner_number:
            delimiter = '-'
        else:
            delimiter = '.'

        return delimiter.join([
            segment.ext_order.number,
            str(self.previous_suffix(segment.ext_order, delimiter) + 1)
        ])

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        waybill_number = self.waybill_number(segment)
        form = self.form_class(initial={
            'doc_number': waybill_number,
            'doc_num_trans': waybill_number,
            'doc_date': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'doc_date_trans': segment.from_date_fact if segment.from_date_fact else segment.from_date_plan,
            'quantity': segment.quantity,
            'weight_brut': segment.weight_brut,
            'value': segment.transit.value
        })
        form.fields.get('doc_type').choices = self.get_types_choices(segment.type)
        return render(request, self.template_name, {'form': form, 'return_url': return_url(request.user, segment)})

    def post(self, request, segment_pk):
        form = self.form_class(data=request.POST)
        segment = TransitSegment.objects.get(pk=segment_pk)
        if form.is_valid():
            wd = form.save(False)
            wd.segment = segment
            wd.save()
            return redirect(return_url(request.user, segment))
        form.fields.get('doc_type').choices = self.get_types_choices(segment.type)
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


class RandomDocScanAddView(View):
    """
    Страница занесения скана иного документа
    """

    def get(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = RandomDocScanForm()
        return render(request, 'print_forms/pages/random_doc_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})

    def post(self, request, segment_pk):
        segment = TransitSegment.objects.get(pk=segment_pk)
        form = RandomDocScanForm(request.POST, request.FILES)
        if form.is_valid():
            orig = form.save(commit=False)
            orig.segment = segment
            orig.transit = segment.transit
            orig.save()
            return redirect(return_url(request.user, segment))
        return render(request, 'print_forms/pages/random_doc_add.html',
                      {'form': form, 'return_url': return_url(request.user, segment)})


class RandomDocScanEdit(UpdateView):
    """
    Страница изменения данных из скана иного документа
    """
    model = RandomDocScan
    form_class = RandomDocScanForm
    template_name = 'print_forms/pages/random_doc_edit.html'

    def get_context_data(self, **kwargs):
        context = super(RandomDocScanEdit, self).get_context_data(**kwargs)
        context['return_url'] = return_url(self.request.user, self.object.segment)
        return context

    def get_success_url(self):
        return return_url(self.request.user, self.object.segment)


class RandomDocScanDelete(DeleteView):
    """
    Страница удаления скана иного документа
    """
    model = RandomDocScan
    template_name = 'print_forms/pages/random_doc_delete.html'

    def get_context_data(self, **kwargs):
        context = super(RandomDocScanDelete, self).get_context_data(**kwargs)
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
        form = super(WaybillPFDataEditView, self).get_form(form_class)
        form.fields.get('doc_type').choices = self.get_types_choices(form.instance.segment.type)
        return form

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
        form = super(TransDocPFDataEditView, self).get_form(form_class)
        form.fields.get('doc_type').choices = self.get_types_choices(form.instance.segment.type)
        return form

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
    return generator.response(f'print_forms/docs/waybill_{docdata.doc_type}.html', context)


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


# def cargo_params(transit):
#     """
#     Коллектор перечня параметров груза для ТН/ЭР
#     """
#     cargos = transit.cargos.all()
#     existing_params = set()
#     for cargo in cargos:
#         for param in cargo.extra_params.all():
#             existing_params.add(str(param))
#
#     result = list()
#
#     if 'Хрупкий' in existing_params:
#         result.append('Хрупкий груз')
#     else:
#         result.append('Не хрупкий груз')
#
#     if 'Опасный' in existing_params:
#         result.append('Опасный груз')
#     else:
#         result.append('Не опасный груз')
#
#     for param in 'Боится влаги', 'Боится деформации':
#         if param in existing_params:
#             result.append(param)
#
#     return '; '.join(result)


def shipping_receipt_ext(request, transit_pk, filename):
    """
    Печатная форма ЭР для заказчика
    """
    transit = Transit.objects.get(pk=transit_pk)
    docs = transit.docs_list.split(', ') if transit.docs_list is not None else None
    context = {
        'transit': transit,
        'order': transit.order,
        'packages': transit.packages,
        'cargo_params': transit.cargo_handling,
        'extra_services': '; '.join([str(i) for i in transit.extra_services.all()]),
        'fax': request.GET.get('fax', False),
        'docs': docs
    }
    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/shipping_receipt_ext.html', context)


def ext_order_blank(request, order_pk, filename):
    """
    Печатная форма исходящего ПЭ
    """
    ext_order = ExtOrder.objects.get(pk=order_pk)
    if ext_order.necessary_docs:
        necessary_docs = ext_order.necessary_docs
    else:
        necessary_docs = ', '.join([dict(DOC_TYPES).get(segment.type) for segment in ext_order.segments.all()])
    context = {
        'ext_order': ext_order,
        'packages': ext_order.transit.packages,
        'necessary_docs': necessary_docs,
        'cargo_params': ext_order.transit.cargo_handling,
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


class BillsBlank(View):
    order_type = None
    fields = [
        'order__contract',
        'order__client_number',
        'order__order_date',
        'sender__short_name',
        'sender__inn',
        'sender__legal_address',
        'from_addr',
        'receiver__short_name',
        'receiver__inn',
        'receiver__legal_address',
        'to_addr',
        'docs_list',
        'from_date_fact',
        'to_date_fact',
        'order__cargo_name',
        'quantity',
        'weight_payed',
        'price_currency',
    ]
    model = None
    bill_field_name = None
    price_field_name = 'price'
    taxes_field_name = 'order__taxes'
    document_template = 'print_forms/docs/bill.html'
    field_overrides = None

    def __init__(self, *args, **kwargs):
        super(BillsBlank, self).__init__(*args, **kwargs)
        self.cookies = None

    def update_cookies(self, request=None):
        if request is None:
            request = self.request
        self.cookies = request.session.get(f'{self.order_type}_bill', {})

    @staticmethod
    def get_value_by_path(obj, path: list):
        value = obj
        for chunk in path:
            value = value.__getattribute__(chunk)
            if callable(value):
                value = value()
        return value

    def get_value(self, obj, field_name):
        if self.field_overrides and field_name in self.field_overrides:
            field_name = self.field_overrides[field_name]
        return self.get_value_by_path(obj, field_name.split('__'))

    def price_and_taxes(self, obj, price_field_name, taxes_rate):
        price = self.get_value(obj, price_field_name)

        if price is not None and taxes_rate is not None:
            taxes_sum = round(price / (100 + taxes_rate) * taxes_rate, 2)
            price_wo_taxes = round(price - taxes_sum, 2)
            return price_wo_taxes, taxes_sum, price
        return price, 'Не применимо', price

    def serialized_obj(self, obj):
        if not self.fields:
            raise NotImplementedError
        result = dict()

        for field_name in self.fields:
            result[field_name] = self.get_value(obj, field_name)

        price_wo_taxes, taxes_sum, price = self.price_and_taxes(
            obj, self.price_field_name,
            self.get_value(obj, self.taxes_field_name)
        )

        result['price_wo_taxes'] = price_wo_taxes
        result['taxes_sum'] = taxes_sum
        result['price'] = price

        return result

    @staticmethod
    def sum_price_and_taxes(obj_list):
        price_wo_taxes = round(sum([i['price_wo_taxes'] for i in obj_list]), 2)
        price = round(sum([i['price'] for i in obj_list]), 2)
        if any([isinstance(i, str) for i in obj_list]):
            taxes_sum = 'Не применимо'
        else:
            taxes_sum = round(sum([i['taxes_sum'] for i in obj_list]), 2)
        return price_wo_taxes, taxes_sum, price

    def get_objects_list(self, queryset):
        return [self.serialized_obj(i) for i in queryset]

    def get(self, request, filename):
        self.update_cookies(request)
        post_data = self.cookies.get('bill_data')
        if post_data is None:
            return redirect('bill_output')
        period = self.cookies.get('period')
        start = datetime.date.fromisoformat(period[0]) if period[0] else None
        end = datetime.date.fromisoformat(period[-1]) if period[-1] else None
        contexts_list = list()
        for bill_number, trans_ids in post_data.items():
            queryset = self.model.objects.filter(pk__in=trans_ids).order_by('order__inner_number')
            queryset.update(**{self.bill_field_name: bill_number if bill_number != 'null' else None})
            obj_list = self.get_objects_list(queryset)
            sum_price_wo_taxes, sum_taxes_sum, sum_price = self.sum_price_and_taxes(obj_list)

            if start is None:
                start = min([i.to_date_fact for i in queryset if i.to_date_fact])

            if end is None:
                end = max([i.to_date_fact for i in queryset if i.to_date_fact])

            contexts_list.append({
                'bill_number': bill_number, 'obj_list': obj_list, 'start': start, 'end': end,
                'sum_price_wo_taxes': sum_price_wo_taxes, 'sum_taxes_sum': sum_taxes_sum, 'sum_price': sum_price
            })
        generator = PDFGenerator(filename)
        return generator.merged_response(self.document_template, contexts_list)


class InternalBillsBlank(BillsBlank):
    order_type = 'internal'
    model = Transit
    bill_field_name = 'bill_number'


class InternationalBillsBlank(BillsBlank):
    order_type = 'international'
    model = ExtOrder
    bill_field_name = 'bill_client'
    price_field_name = 'price_client'
    field_overrides = {
        'price_currency': 'currency_client',
        'quantity': 'transit__quantity'
    }


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
        queryset = Transit.objects.filter(pk__in=trans_ids).order_by('order__inner_number')
        queryset.update(bill_number=bill_number if bill_number != 'null' else None)
        contexts_list.append({
            'bill_number': bill_number, 'queryset': queryset, 'start': start, 'end': end,
            'sum_price_wo_taxes': round(sum([i.price_wo_taxes() for i in queryset if i.price]), 2),
            'sum_taxes_sum': round(sum([i.taxes_sum() for i in queryset if not isinstance(i.taxes_sum(), str)]), 2),
            'sum_price': round(sum([i.price for i in queryset if i.price]), 2)
        })
    generator = PDFGenerator(filename)
    return generator.merged_response('print_forms/docs/bill.html', contexts_list)


def get_senders_list(transits):
    senders = list()
    for transit in transits:
        if transit.sender not in senders:
            senders.append(transit.sender)
    if len(senders) == 1:
        return {'sender_single': senders[0]}
    return {'senders': senders}


def get_receivers_list(transits):
    receivers = list()
    for transit in transits:
        if transit.receiver not in receivers:
            receivers.append(transit.receiver)
    if len(receivers) == 1:
        return {'receiver_single': receivers[0]}
    return {'receivers': receivers}


def transit_departure_context(transit):
    return {
        'from_addr': transit.from_addr,
        'from_contacts': '; '.join([i.full_output() for i in transit.from_contacts.all()]),
        'from_date_wanted': transit.from_date_wanted
    }


def transit_arrival_context(transit):
    return {
        'to_addr': transit.to_addr,
        'to_contacts': '; '.join([i.full_output() for i in transit.to_contacts.all()]),
    }


def get_departure_data_list(transits):
    departures = list()
    for transit in transits:
        context = transit_departure_context(transit)
        if context not in departures:
            departures.append(context)
    if len(departures) == 1:
        return {'departure_single': departures[0]}
    return {'departures': departures}


def get_arrival_data_list(transits):
    arrivals = list()
    for transit in transits:
        context = transit_arrival_context(transit)
        if context not in arrivals:
            arrivals.append(context)
    if len(arrivals) == 1:
        return {'arrival_single': arrivals[0]}
    return {'arrivals': arrivals}


def get_transit_types_list(transits):
    types = list()
    for transit in transits:
        if transit.type is not None and transit.type not in types:
            types.append(transit.type)
    if len(types) == 1:
        return {'type_single': types[0]}
    else:
        return {'types': types}


def get_packages_list(transits):
    packages = list()
    for transit in transits:
        cargos = transit.cargos.all().values_list('package_type', flat=True).distinct()
        packages_verbose = dict(Cargo.PACKAGE_TYPES)
        cargos_verbose = [packages_verbose[i] for i in cargos]
        packages.append(f'{", ".join(cargos_verbose)} - {transit.quantity} шт.')
    if len(packages) == 1:
        return {'package_single': packages[0]}
    else:
        return {'packages': packages}


def get_weights_list(transits):
    weights = transits.values_list('weight', flat=True)
    if len(weights) == 1:
        return {'weight_single': weights[0]}
    else:
        return {'weights': weights}


def get_values_list(transits):
    values = transits.values_list('value', 'currency')
    if len(values) == 1:
        return {'value_single': values[0]}
    else:
        return {'values': values}


def transit_route_context(transit):
    extra_services = transit.extra_services.all().values_list('machine_name', flat=True)
    extra_cargo_params = transit.cargos.all().values_list('extra_params__machine_name', flat=True).distinct()
    requirements_raw = list(set(list(extra_services) + list(extra_cargo_params)))
    requirements = list()

    if 'fragile' in requirements_raw:
        requirements.append('хрупкий')

    if 'dangerous' in requirements_raw:
        requirements.append('опасный груз')
    else:
        requirements.append('не опасный груз')

    if 'deform' in requirements_raw:
        requirements.append('боится деформации')

    if 'moisture' in requirements_raw:
        requirements.append('боится влаги')

    if 'do_not_stack' in requirements_raw:
        requirements.append('штабелировать нельзя')
    else:
        requirements.append('штабелировать можно')

    if 'do_not_turn_over' in requirements_raw:
        requirements.append('кантовать нельзя')
    else:
        requirements.append('кантовать можно')

    if 'temperature' in requirements_raw:
        requirements.append('требуется соблюдение температурного режима')

    if 'crate_required' in requirements_raw:
        requirements.append('требуется обрешетка')

    if 'tie_down_straps' in requirements_raw:
        requirements.append('требуется наличие стяжных ремней')

    if 'special_fasteners' in requirements_raw:
        requirements.append('требуется наличие специального крепежа')

    requirements = ', '.join(requirements).capitalize()

    return {
        'from_addr': transit.from_addr,
        'to_addr': transit.to_addr,
        'requirements': requirements
    }


def get_routes_list(transits):
    routes = [transit_route_context(i) for i in transits]
    if len(routes) == 1:
        return {'route_single': routes[0]}
    else:
        return {'routes': routes}


def order_blank(request, order_pk, filename):
    """
    Печатная форма входящего поручения
    """
    order = Order.objects.get(pk=order_pk)
    transits = order.transits.all()
    context = {
        'order': order,
        'transits': transits
    }

    context.update(get_senders_list(transits))
    context.update(get_receivers_list(transits))
    context.update(get_departure_data_list(transits))
    context.update(get_arrival_data_list(transits))
    context.update(get_transit_types_list(transits))
    context.update(get_packages_list(transits))
    context.update(get_weights_list(transits))
    context.update(get_values_list(transits))
    context.update(get_routes_list(transits))
    context['aero'] = 'авиа' in context.get('type_single', '').lower() + ''.join(context.get('types', [])).lower()

    generator = PDFGenerator(filename)
    return generator.response('print_forms/docs/order_blank.html', context)
