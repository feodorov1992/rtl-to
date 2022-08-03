import csv
import datetime
import json
import uuid
from io import StringIO, TextIOWrapper, BufferedWriter, RawIOBase, BufferedIOBase, FileIO

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms import DateInput, CheckboxSelectMultiple
from django.forms.models import ModelChoiceIterator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.forms import CounterpartySelectForm, AuditorForm
from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client, Contractor, Auditor, ReportParams
from configs.groups_perms import get_or_init
from management.forms import UserAddForm, UserEditForm, OrderEditTransitFormset, OrderCreateTransitFormset, \
    OrderListFilters, AgentAddForm, ReportsForm, ReportsFilterForm
from management.serializers import FieldsMapper

from orders.forms import OrderStatusFormset, TransitStatusFormset, TransitSegmentFormset, OrderForm, FileUploadFormset
from orders.models import Order, OrderHistory, Transit, TransitHistory, TransitSegment


@permission_required(perm=['app_auth.view_all_clients', 'app_auth.view_all_users'], login_url='login')
def dashboard(request):
    all_orders = Order.objects.all()
    active_orders = all_orders.exclude(status__in=['completed', 'rejected'])
    late_orders = active_orders.filter(to_date_plan__lt=datetime.date.today())

    all_transits = Transit.objects.all()
    active_transits = all_orders.exclude(status__in=['completed', 'rejected'])
    late_transits = active_orders.filter(to_date_plan__lt=datetime.date.today())

    all_users = User.objects.all()
    active_users = all_users.filter(is_active=True)
    all_clients = Client.objects.all()
    all_contractors = Contractor.objects.all()

    context = {
        'all_orders': all_orders.count(),
        'active_orders': active_orders.count(),
        'late_orders': late_orders.count(),

        'all_transits': all_transits.count(),
        'active_transits': active_transits.count(),
        'late_transits': late_transits.count(),

        'all_users': all_users.count(),
        'active_users': active_users.count(),
        'all_clients': all_clients.count(),
        'all_contractors': all_contractors.count(),
    }

    return render(request, 'management/dashboard.html', context)


class ClientsListView(PermissionRequiredMixin, ListView):
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Client
    template_name = 'management/clients_list.html'


class AuditorsListView(PermissionRequiredMixin, ListView):
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditors_list.html'


class ClientDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Client
    template_name = 'management/client_detail.html'


class AuditorDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditor_detail.html'


class ClientAddView(PermissionRequiredMixin, CreateView):
    permission_required = 'app_auth.add_client'
    login_url = 'login'
    model = Client
    fields = '__all__'
    template_name = 'management/client_add.html'

    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ClientAddView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['contract_sign_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        form.fields['contract_expiration_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        return form


class AuditorAddView(PermissionRequiredMixin, CreateView):
    permission_required = 'app_auth.add_client'
    login_url = 'login'
    model = Auditor
    form_class = AuditorForm
    template_name = 'management/auditor_add.html'

    def get_success_url(self):
        return reverse('auditor_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(AuditorAddView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['controlled_clients'].widget = CheckboxSelectMultiple()
        form.fields['controlled_clients'].widget.choices = ModelChoiceIterator(form.fields['controlled_clients'])
        return form


class ClientEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app_auth.change_client'
    login_url = 'login'
    model = Client
    fields = '__all__'
    template_name = 'management/client_edit.html'

    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ClientEditView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['contract_sign_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        form.fields['contract_expiration_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        return form


class AuditorEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app_auth.change_client'
    login_url = 'login'
    model = Auditor
    form_class = AuditorForm
    template_name = 'management/auditor_edit.html'

    def get_success_url(self):
        return reverse('auditor_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(AuditorEditView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['controlled_clients'].widget = CheckboxSelectMultiple()
        form.fields['controlled_clients'].widget.choices = ModelChoiceIterator(form.fields['controlled_clients'])
        return form


class ClientDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'app_auth.delete_client'
    login_url = 'login'
    model = Client
    template_name = 'management/client_delete.html'

    def get_success_url(self):
        return reverse('clients_list')


class AuditorDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'app_auth.delete_client'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditor_delete.html'

    def get_success_url(self):
        return reverse('auditors_list')


class ContractorListView(PermissionRequiredMixin, ListView):
    permission_required = 'app_auth.view_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractors_list.html'


class ContractorAddView(PermissionRequiredMixin, CreateView):
    permission_required = 'app_auth.add_contractor'
    login_url = 'login'
    model = Contractor
    fields = '__all__'
    template_name = 'management/contractor_add.html'

    def get_success_url(self):
        return reverse('contractor_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ContractorAddView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['contract_sign_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        form.fields['contract_expiration_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        return form


class ContractorDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'app_auth.view_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractor_detail.html'


class ContractorEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app_auth.change_contractor'
    login_url = 'login'
    model = Contractor
    fields = '__all__'
    template_name = 'management/contractor_edit.html'

    def get_success_url(self):
        return reverse('contractor_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(ContractorEditView, self).get_form(form_class)
        form.required_css_class = 'required'
        form.fields['contract_sign_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        form.fields['contract_expiration_date'].widget = DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        return form


class ContractorDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'app_auth.delete_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractor_delete.html'

    def get_success_url(self):
        return reverse('contractors_list')


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'app_auth.view_all_users'
    login_url = 'login'
    model = User
    template_name = 'management/user_list.html'


class UserDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'app_auth.view_all_users'
    login_url = 'login'
    model = User
    template_name = 'management/user_detail.html'


class UserAddView(PermissionRequiredMixin, View):
    permission_required = ['app_auth.view_all_users', 'app_auth.add_user']
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        if request.GET.get('client'):
            clients = Client.objects.filter(id=request.GET.get('client'))
            if clients.exists():
                client = clients.last()
                form.fields['client'].initial = client
        return render(request, 'management/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user_type = form.cleaned_data['user_type']
            user.groups.add(get_or_init(user_type))
            if user_type == 'STAFF_USER':
                user.is_staff = True
            else:
                user.is_staff = False
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('users_list')
        return render(request, 'management/user_add.html', {'form': form})


class AgentAddView(PermissionRequiredMixin, View):
    permission_required = ['app_auth.view_all_users', 'app_auth.add_user']
    login_url = 'login'

    def get(self, request):
        form = AgentAddForm()
        if request.GET.get('auditor'):
            auditors = Auditor.objects.filter(id=request.GET.get('auditor'))
            if auditors.exists():
                auditor = auditors.last()
                form.fields['auditor'].initial = auditor
        return render(request, 'management/agent_add.html', {'form': form})

    def post(self, request):
        form = AgentAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user_type = form.cleaned_data['user_type']
            user.groups.add(get_or_init(user_type))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('auditor_detail', pk=user.auditor.pk)
        return render(request, 'management/agent_add.html', {'form': form})


class UserEditView(PermissionRequiredMixin, View):
    permission_required = ['app_auth.view_all_users', 'app_auth.change_user']

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(instance=user)
        form.fields['user_type'].initial = list(user.groups.all().values_list('name', flat=True))
        return render(request, 'management/user_edit.html', {'form': form})

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user.groups.clear()
            user_type = form.cleaned_data['user_type']
            user.groups.add(get_or_init(user_type))
            if user_type == 'STAFF_USER':
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
            form.save()
            return redirect(request.GET['next'])
        return render(request, 'management/user_edit.html', {'form': form})


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ['app_auth.view_all_users', 'app_auth.delete_user']
    login_url = 'login'
    model = User
    template_name = 'management/user_delete.html'

    def get_success_url(self):
        return reverse('users_list')


class OrderListView(PermissionRequiredMixin, FilteredListView):
    permission_required = 'orders.view_all_orders'
    login_url = 'login'
    model = Order
    form_class = OrderListFilters
    template_name = 'management/order_list.html'
    paginate_by = 10

    search_fields = ['inner_number', 'client_number']
    filter_fields = ['client', 'type', 'manager', 'status']
    filter_optional = ['manager']
    default_order = '-order_date'

    def get_filters(self):
        filters = super(OrderListView, self).get_filters()
        for f in filters:
            if f.name in self.filter_optional:
                value = self.form.cleaned_data.get(f.name)
                for choice in f.choices:
                    if choice.value == value or (choice.value == '' and value is None):
                        choice.is_selected = True
        return filters

    def form_valid(self, form):
        force_empty = {}
        for fn in self.filter_optional:
            if form.cleaned_data.get(fn) == 'none':
                form.cleaned_data.pop(fn)
                force_empty[fn] = None
        queryset = super(OrderListView, self).form_valid(form)
        queryset = queryset.filter(**force_empty)
        for fn in force_empty:
            form.cleaned_data[fn] = 'none'

        if form.cleaned_data['from_date']:
            queryset = queryset.filter(created_at__gte=form.cleaned_data['from_date'])
        if form.cleaned_data['to_date']:
            queryset = queryset.filter(created_at__lte=form.cleaned_data['to_date'])
        return queryset


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ['orders.view_order', 'orders.view_all_orders']
    login_url = 'login'
    model = Order
    template_name = 'management/order_detail.html'


class OrderHistoryView(PermissionRequiredMixin, DetailView):
    permission_required = ['orders.view_order', 'orders.view_all_orders']
    login_url = 'login'
    model = Order
    template_name = 'management/order_history.html'


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'orders.delete_order'
    login_url = 'login'
    model = Order
    template_name = 'management/order_delete.html'

    def get_success_url(self):
        return reverse('orders_list')


class OrderEditView(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order_form = OrderForm(instance=order)
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client).order_by('last_name', 'first_name')
        order_form.fields['manager'].queryset = User.objects.filter(client=None).order_by('last_name', 'first_name')
        transits = OrderEditTransitFormset(instance=order)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'order': order, 'transits': transits})

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        order_form = OrderForm(request.POST, instance=order)
        transits = OrderEditTransitFormset(request.POST, instance=order)
        if transits.is_valid() and order_form.is_valid():

            order_form.save()
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            return redirect('order_detail', pk=pk)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'order': order, 'transits': transits})


class OrderCreateView(PermissionRequiredMixin, View):
    permission_required = ['orders.add_order', 'orders.view_all_orders']
    login_url = 'login'

    def get(self, request):
        order_form = OrderForm()
        transits = OrderCreateTransitFormset()
        return render(request, 'management/order_add.html',
                      {'order_form': order_form, 'transits': transits})

    def post(self, request):
        order_form = OrderForm(request.POST)
        transits = OrderCreateTransitFormset(request.POST)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save()
            transits.instance = order
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            return redirect('order_detail', pk=order.pk)
        print(order_form.errors)
        print(transits.errors)
        return render(request, 'management/order_add.html',
                      {'order_form': order_form, 'transits': transits})


class OrderHistoryEditView(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        status_formset = OrderStatusFormset(instance=order)
        return render(request, 'management/status_list_edit.html', {'status_formset': status_formset})

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        status_formset = OrderStatusFormset(request.POST, instance=order)
        if status_formset.is_valid():
            for cd in status_formset.cleaned_data:
                if not cd:
                    OrderHistory(order=order).save()
            status_formset.save()
            return redirect('order_detail', pk=pk)
        return render(request, 'management/status_list_edit.html', {'status_formset': status_formset})


class TransitHistoryEditView(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        status_formset = TransitStatusFormset(instance=transit)
        return render(request, 'management/status_list_edit.html', {'status_formset': status_formset})

    def post(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        status_formset = TransitStatusFormset(request.POST, instance=transit)
        if status_formset.is_valid():
            for cd in status_formset.cleaned_data:
                if not cd:
                    TransitHistory(transit=transit).save()
            status_formset.save()
            return redirect('order_detail', pk=transit.order.pk)
        return render(request, 'management/status_list_edit.html', {'status_formset': status_formset})


class SegmentsEditView(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        segment_formset = TransitSegmentFormset(instance=transit)
        return render(request, 'management/segments_list_edit.html', {'segment_formset': segment_formset})

    def post(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        segment_formset = TransitSegmentFormset(request.POST, instance=transit)
        if segment_formset.is_valid():
            segment_formset.save()
            return redirect('order_detail', pk=transit.order.pk)
        return render(request, 'management/segments_list_edit.html', {'segment_formset': segment_formset})


class ManagerGetOrderView(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.manager = request.user
        order.save()
        return redirect(request.GET.get('next', 'orders_list'))


class OrderFileUpload(PermissionRequiredMixin, View):
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        docs_formset = FileUploadFormset(instance=order)
        return render(request, 'management/docs_list_edit.html', {'docs_formset': docs_formset})

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        docs_formset = FileUploadFormset(request.POST, request.FILES, instance=order)
        if docs_formset.is_valid():
            docs_formset.save()
            return redirect('order_detail', pk=pk)
        return render(request, 'management/docs_list_edit.html', {'docs_formset': docs_formset})


REPORT_MODEL_ROUTER = {
    'segment': TransitSegment,
    'transit': Transit,
    'order': Order
}


class ReportsCreateView(View):
    def post(self, request):
        if request.POST.get('merge_segments') == 'on':
            merge = True
        else:
            merge = False
        report = ReportParams(
            name=request.POST.get('report_name'),
            order_fields=request.POST.getlist('order_fields'),
            transit_fields=request.POST.getlist('transit_fields'),
            segment_fields=request.POST.getlist('segment_fields'),
            merge_segments=merge,
            user=request.user
        )

        try:
            report.save()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports') + f'?report={report.pk}'
            }))
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportUpdateView(View):

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        report.order_fields = request.POST.getlist('order_fields')
        report.transit_fields = request.POST.getlist('transit_fields')
        report.segment_fields = request.POST.getlist('segment_fields')

        if request.POST.get('merge_segments') == 'on':
            merge = True
        else:
            merge = False

        report.merge_segments = merge

        try:
            report.save()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports') + f'?report={report.pk}'
            }))
        except Exception as e:
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportDeleteView(View):

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        try:
            report.delete()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports')
            }))
        except Exception as e:
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportsView(View):

    def get(self, request):
        fields_form = ReportsForm()
        filter_form = ReportsFilterForm()
        report_pk = request.GET.get('report')
        if report_pk:
            report = ReportParams.objects.filter(pk=report_pk)
            if report.exists():
                report = report.last()
                fields_form.fields['order_fields'].initial = report.order_fields
                fields_form.fields['transit_fields'].initial = report.transit_fields
                fields_form.fields['segment_fields'].initial = report.segment_fields
                fields_form.fields['merge_segments'].initial = report.merge_segments
        else:
            fields_form.select_all()
        saved_reports = request.user.reports.all()
        return render(request, 'management/reports.html', {
            'fields_form': fields_form, 'filter_form': filter_form, 'saved_reports': saved_reports
        })

    @staticmethod
    def create_csv(data, header):
        file = StringIO()
        wr = csv.writer(file, delimiter=';')
        wr.writerow(header)
        wr.writerows(data)
        response = HttpResponse(file.getvalue().encode('cp1251'), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'
        return response

    def post(self, request):
        saved_reports = request.user.reports.all()
        fields_form = ReportsForm(data=request.POST)
        filter_form = ReportsFilterForm(data=request.POST)
        if fields_form.is_valid():
            order_fields = fields_form.cleaned_data.get('order_fields')
            transit_fields = fields_form.cleaned_data.get('transit_fields')
            segment_fields = fields_form.cleaned_data.get('segment_fields')
            merge_segments = fields_form.cleaned_data.get('merge_segments')
            mapper = FieldsMapper()
            mapper.collect_fields_data(
                order_fields=order_fields,
                order_filters=filter_form.serialized_result('order'),
                transit_fields=transit_fields,
                transit_filters=filter_form.serialized_result('transit'),
                segment_fields=segment_fields,
                segment_filters=filter_form.serialized_result('segment'),
                merge_segments=merge_segments
            )
            if fields_form.cleaned_data.get('report_type') == 'csv':
                csv_data, header = mapper.csv_output()
                return self.create_csv(csv_data, header)
            objects, fields_verbose, fields_counter = mapper.web_output()
            return render(request, 'management/reports.html', {
                'fields_form': fields_form, 'filter_form': filter_form, 'objects': objects, 'fields': fields_verbose,
                'saved_reports': saved_reports, 'fields_counter': fields_counter
            })
        return render(request, 'management/reports.html', {
            'fields_form': fields_form, 'filter_form': filter_form, 'saved_reports': saved_reports
        })
