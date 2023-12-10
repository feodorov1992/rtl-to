import csv
import datetime
import json
import logging
import uuid
from io import StringIO, BytesIO

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.db import models
from django.forms import DateInput, CheckboxSelectMultiple
from django.forms.models import ModelChoiceIterator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.forms import AuditorForm, ContractorContractForm, ClientContractForm
from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client, Contractor, Auditor, ReportParams, ContractorContract, ClientContract
from configs.groups_perms import get_or_init
from management.forms import UserAddForm, UserEditForm, OrderEditTransitFormset, OrderCreateTransitFormset, \
    OrderListFilters, ReportsForm, ReportsFilterForm, BillOutputForm, ExtOrderListFilters1, \
    InternationalOrderCreateTransitFormset, InternationalOrderEditTransitFormset, BillOutputSearchForm
from management.reports import ReportGenerator
from orders.forms import OrderStatusFormset, TransitStatusFormset, OrderForm, FileUploadFormset, ExtOrderFormset
from orders.mailer import order_assigned_to_manager, order_assigned_to_manager_for_client
from orders.models import Order, OrderHistory, Transit, TransitHistory, TransitSegment, Cargo, ExtOrder
import xlwt

logger = logging.getLogger(__name__)


@permission_required(perm=['app_auth.view_all_clients', 'app_auth.view_all_users'], login_url='login')
def dashboard(request):
    """
    Страница "Общая информация"
    """
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
    """
    Страница "Заказчики"
    """
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Client
    template_name = 'management/clients_list.html'


class AuditorsListView(PermissionRequiredMixin, ListView):
    """
    Страница "Аудиторы"
    """
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditors_list.html'


class ClientDetailView(PermissionRequiredMixin, DetailView):
    """
    Карточка организации-заказчика (просмотр)
    """
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Client
    template_name = 'management/client_detail.html'


class AuditorDetailView(PermissionRequiredMixin, DetailView):
    """
    Карточка организации-аудитора (просмотр)
    """
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditor_detail.html'


class ClientAddView(PermissionRequiredMixin, CreateView):
    """
    Страница добавлкния организации-заказчика
    """
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
        return form


class AuditorAddView(PermissionRequiredMixin, CreateView):
    """
    Страница добавлкния организации-аудитора
    """
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
    """
    Страница изменения организации-заказчика
    """
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
        return form


class AuditorEditView(PermissionRequiredMixin, UpdateView):
    """
    Страница изменения организации-аудитора
    """
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
    """
    Страница удаления организации-заказчика
    """
    permission_required = 'app_auth.delete_client'
    login_url = 'login'
    model = Client
    template_name = 'management/client_delete.html'

    def get_success_url(self):
        return reverse('clients_list')


class ClientContractAddFullView(View):
    template_name = 'management/contract_add_full.html'
    owner_detail_url_name = 'client_detail'

    def get(self, request, pk):
        client = Client.objects.get(pk=pk)
        form = ClientContractForm()
        return render(request, 'management/contract_add_full.html',
                      {'form': form, 'owner': client,
                       'owner_detail_url': reverse(self.owner_detail_url_name, kwargs={'pk': str(client.pk)})})

    def post(self, request, pk):
        client = Client.objects.get(pk=pk)
        form = ClientContractForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(False)
            obj.client = client
            obj.save()
            return redirect(self.owner_detail_url_name, pk=client.pk)
        return render(request, 'management/contract_add_full.html',
                      {'form': form, 'owner': client,
                       'owner_detail_url': reverse(self.owner_detail_url_name, kwargs={'pk': str(client.pk)})})


class ClientContractEditFullView(UpdateView):
    template_name = 'management/contract_edit_full.html'
    model = ClientContract
    form_class = ClientContractForm

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs.get('contract_pk'))

    def get_context_data(self, **kwargs):
        context = super(ClientContractEditFullView, self).get_context_data(**kwargs)
        context['owner_detail_url'] = reverse('client_detail', kwargs={'pk': self.kwargs.get('pk')})
        return context

    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.kwargs.get('pk')})


class AuditorDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Страница удаления организации-аудитора
    """
    permission_required = 'app_auth.delete_client'
    login_url = 'login'
    model = Auditor
    template_name = 'management/auditor_delete.html'

    def get_success_url(self):
        return reverse('auditors_list')


class ContractorListView(PermissionRequiredMixin, ListView):
    """
    Страница "Подрядчики"
    """
    permission_required = 'app_auth.view_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractors_list.html'


class ContractorAddView(PermissionRequiredMixin, CreateView):
    """
    Страница добавления подрядчика
    """
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
        return form


class ContractorDetailView(PermissionRequiredMixin, DetailView):
    """
    Карточка организации-подрядчика (просмотр)
    """
    permission_required = 'app_auth.view_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractor_detail.html'


class ContractorContractAddFullView(View):
    template_name = 'management/contract_add_full.html'
    model = ContractorContract
    form_class = ContractorContractForm
    owner_detail_url_name = 'contractor_detail'

    def get(self, request, pk):
        contractor = Contractor.objects.get(pk=pk)
        form = ContractorContractForm()
        return render(request, 'management/contract_add_full.html',
                      {'form': form, 'owner': contractor,
                       'owner_detail_url': reverse(self.owner_detail_url_name, kwargs={'pk': str(contractor.pk)})})

    def post(self, request, pk):
        contractor = Contractor.objects.get(pk=pk)
        form = ContractorContractForm(request.POST)
        if form.is_valid():
            obj = form.save(False)
            obj.contractor = contractor
            obj.update_current_sum()
            return redirect(self.owner_detail_url_name, pk=contractor.pk)
        return render(request, 'management/contract_add_full.html',
                      {'form': form, 'owner': contractor,
                       'owner_detail_url': reverse(self.owner_detail_url_name, kwargs={'pk': str(contractor.pk)})})


class ContractorContractEditFullView(UpdateView):
    template_name = 'management/contract_edit_full.html'
    model = ContractorContract
    form_class = ContractorContractForm

    def get_context_data(self, **kwargs):
        context = super(ContractorContractEditFullView, self).get_context_data(**kwargs)
        context['owner_detail_url'] = reverse('contractor_detail', kwargs={'pk': self.kwargs.get('pk')})
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs.get('contract_pk'))

    def get_success_url(self):
        return reverse('contractor_detail', kwargs={'pk': self.kwargs.get('pk')})


class ContractorEditView(PermissionRequiredMixin, UpdateView):
    """
    Страница изменения подрядчика
    """
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
        return form


class ContractorDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Страница удаления подрядчика
    """
    permission_required = 'app_auth.delete_contractor'
    login_url = 'login'
    model = Contractor
    template_name = 'management/contractor_delete.html'

    def get_success_url(self):
        return reverse('contractors_list')


class UserListView(PermissionRequiredMixin, ListView):
    """
    Страница "Пользователи"
    """
    permission_required = 'app_auth.view_all_users'
    login_url = 'login'
    model = User
    template_name = 'management/user_list.html'


class UserDetailView(PermissionRequiredMixin, DetailView):
    """
    Карточка пользователя
    """
    permission_required = 'app_auth.view_all_users'
    login_url = 'login'
    model = User
    template_name = 'management/user_detail.html'


class UserAddView(PermissionRequiredMixin, View):
    """
    Страница добавления пользователя
    """
    permission_required = ['app_auth.view_all_users', 'app_auth.add_user']
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        for org_type in ['client', 'auditor', 'contractor']:
            org_id = request.GET.get(org_type)
            if org_id is not None:
                org_class = globals().get(org_type.capitalize())
                orgs = org_class.objects.filter(id=org_id)
                if orgs.exists():
                    form.fields[org_type].initial = orgs.last()
                    form.fields['user_type'].initial = f'{org_type}_advanced'
        return render(request, 'management/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.groups.add(get_or_init(user.user_type))
            if user.user_type == 'manager':
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


def resend_registration_mail(request, pk):
    """
    Кнопка "Отправить письмо повторно"
    """
    user = User.objects.get(pk=pk)
    send_technical_mail(
        request, user,
        subject='Подтверждение регистрации',
        link_name='registration_confirm',
        mail_template='app_auth/mail/acc_active_email.html'
    )
    next_url = request.GET.get('next')
    if next_url is not None:
        return redirect(next_url)
    return redirect('users_list')


class AgentAddView(PermissionRequiredMixin, View):
    """
    Страница добавления сотрудника аудитора
    """
    permission_required = ['app_auth.view_all_users', 'app_auth.add_user']
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        if request.GET.get('auditor'):
            auditors = Auditor.objects.filter(id=request.GET.get('auditor'))
            if auditors.exists():
                auditor = auditors.last()
                form.fields['auditor'].initial = auditor
                form.fields['user_type'].initial = 'auditor_advanced'
        return render(request, 'management/agent_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.groups.add(get_or_init(user.user_type))
            user.is_active = False
            if user.user_type == 'manager':
                user.is_staff = True
            else:
                user.is_staff = False
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
    """
    Страница изменения пользователя
    """
    permission_required = ['app_auth.view_all_users', 'app_auth.change_user']

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(instance=user)
        return render(request, 'management/user_edit.html', {'form': form})

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user.groups.clear()
            user.groups.add(get_or_init(user.user_type))
            if user.user_type == 'manager':
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
            form.save()
            return redirect(request.GET['next'])
        return render(request, 'management/user_edit.html', {'form': form})


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Страница удаления пользователя
    """
    permission_required = ['app_auth.view_all_users', 'app_auth.delete_user']
    login_url = 'login'
    model = User
    template_name = 'management/user_delete.html'

    def get_success_url(self):
        return reverse('users_list')


class OrderListView(PermissionRequiredMixin, FilteredListView):
    """
    Страница "Поручения"
    """
    permission_required = 'orders.view_all_orders'
    login_url = 'login'
    model = Order
    form_class = OrderListFilters
    template_name = 'management/order_list.html'
    paginate_by = 10

    search_fields = ['inner_number', 'client_number']
    filter_fields = ['client', 'type', 'manager', 'status']
    filter_optional = ['manager']

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
    """
    Страница детализации поручения
    """
    permission_required = ['orders.view_order', 'orders.view_all_orders']
    login_url = 'login'
    model = Order
    template_name = 'management/order_detail.html'


class OrderHistoryView(PermissionRequiredMixin, DetailView):
    """
    Страница с историей статусов поручения
    """
    permission_required = ['orders.view_order', 'orders.view_all_orders']
    login_url = 'login'
    model = Order
    template_name = 'management/order_history.html'


class OrderDeleteView(PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Страница удаления поручения
    """
    permission_required = 'orders.delete_order'
    login_url = 'login'
    model = Order
    template_name = 'management/order_delete.html'

    def test_func(self):
        obj = self.get_object(self.queryset)
        return self.request.user == obj.manager

    def get_success_url(self):
        return reverse('orders_list')


class OrderEditView(PermissionRequiredMixin, View):
    """
    Страница редактирования поручения
    """
    permission_required = 'orders.change_order'
    login_url = 'login'
    order_form_class = OrderForm
    transits_formset_class = OrderEditTransitFormset
    template = 'management/order_edit.html'
    order_type = 'internal'

    def test_func(self):
        return self.request.user == self.object.manager

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user != order.manager:
            return redirect('order_detail', pk=pk)
        order_form = self.order_form_class(instance=order)
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client)
        order_form.fields['manager'].queryset = User.objects.filter(user_type='manager')
        transits = self.transits_formset_class(instance=order)
        return render(request, self.template, {'order_form': order_form, 'order': order, 'transits': transits})

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user != order.manager:
            return redirect('order_detail', pk=pk)
        data = request.POST.copy()
        if order.created_by:
            data['created_by'] = order.created_by.pk
        order_form = self.order_form_class(data, instance=order)
        transits = self.transits_formset_class(data, instance=order)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_type = self.order_type
            order.save()
            if 'manager' in order_form.changed_data and order_form.cleaned_data.get('manager') is not None:
                order_assigned_to_manager(request, order)
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            else:
                order.enumerate_transits()
            return redirect('order_detail', pk=pk)
        if order_form.errors:
            logger.error(f'Order errors: {order_form.errors}')
        if transits.errors:
            logger.error(f'Transits errors: {transits.errors}')
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client)
        return render(request, self.template, {'order_form': order_form, 'order': order, 'transits': transits})


class InternationalOrderEditView(OrderEditView):
    """
    Страница редактирования международного поручения
    """
    transits_formset_class = InternationalOrderEditTransitFormset
    order_type = 'international'
    # template = 'management/order_edit_international.html'


class OrderCreateView(PermissionRequiredMixin, View):
    """
    Страница добавления нового поручения
    """
    permission_required = ['orders.add_order', 'orders.view_all_orders']
    login_url = 'login'
    order_form_class = OrderForm
    transits_formset_class = OrderCreateTransitFormset
    template = 'management/order_add.html'
    order_type = 'internal'

    def get(self, request):
        order_form = self.order_form_class()
        order_form.fields['client_employee'].queryset = User.objects.none()
        transits = self.transits_formset_class()
        return render(request, self.template,
                      {'order_form': order_form, 'transits': transits})

    def post(self, request):
        data = request.POST.copy()
        data['created_by'] = request.user.pk
        order_form = self.order_form_class(data)
        transits = self.transits_formset_class(data)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save(commit=False)
            order.type = self.order_type
            order.save()
            transits.instance = order
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            else:
                order.enumerate_transits()
            return redirect('order_detail', pk=order.pk)
        if order_form.errors:
            logger.error(f'Order errors: {order_form.errors}')
        if transits.errors:
            logger.error(f'Transits errors: {transits.errors}')
        order_form.fields['client_employee'].queryset = User.objects.none()
        return render(request, self.template,
                      {'order_form': order_form, 'transits': transits})


class InternationalOrderCreateView(OrderCreateView):
    """
    Страница добавления нового поручения
    """
    transits_formset_class = InternationalOrderCreateTransitFormset
    order_type = 'international'


class OrderHistoryEditView(PermissionRequiredMixin, View):
    """
    Страница редактирования истории статусов поручения
    """
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
    """
    Страница редактирования истории статусов перевозки
    """
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


class ExtOrderEditView(PermissionRequiredMixin, View):
    """
    Страница управления исходящими поручениями
    """
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        if request.user != transit.order.manager:
            return redirect('order_detail', pk=transit.order.pk)
        ext_orders_formset = ExtOrderFormset(instance=transit,
                                             segments_initials={
                                                 'quantity': transit.quantity,
                                                 'weight_payed': transit.weight,
                                                 'weight_brut': transit.weight
                                             },
                                             initials={
                                                 'from_addr': transit.from_addr,
                                                 'from_addr_short': transit.from_addr_short,
                                                 'from_addr_eng': transit.from_addr_eng,
                                                 'to_addr': transit.to_addr,
                                                 'to_addr_short': transit.to_addr_short,
                                                 'to_addr_eng': transit.to_addr_eng,
                                                 'sender': transit.sender,
                                                 'from_contacts': transit.from_contacts,
                                                 'receiver': transit.receiver,
                                                 'to_contacts': transit.to_contacts,
                                                 'take_from': transit.take_from,
                                                 'give_to': transit.give_to,
                                                 'from_date_wanted': transit.from_date_wanted,
                                                 'to_date_wanted': transit.to_date_wanted,
                                                 'manager': request.user
                                             })
        delimiter = '-' if transit.number == transit.order.inner_number else '.'
        return render(request, 'management/ext_orders_list_edit.html', {'ext_orders_formset': ext_orders_formset,
                                                                        'delimiter': delimiter})

    def post(self, request, pk):
        transit = Transit.objects.get(pk=pk)
        if request.user != transit.order.manager:
            return redirect('order_detail', pk=transit.order.pk)
        ext_orders_formset = ExtOrderFormset(request.POST, instance=transit)
        if ext_orders_formset.is_valid():
            ext_orders_formset.save()
            transit.enumerate_ext_orders()
            return redirect('order_detail', pk=transit.order.pk)
        return render(request, 'management/ext_orders_list_edit.html', {'ext_orders_formset': ext_orders_formset})


class ManagerGetOrderView(PermissionRequiredMixin, View):
    """
    Кнопка "Взять в работу"
    """
    permission_required = 'orders.change_order'
    login_url = 'login'

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.manager = request.user
        order.save()
        order_assigned_to_manager_for_client(request, order)
        return redirect(request.GET.get('next', 'orders_list'))


class OrderFileUpload(PermissionRequiredMixin, View):
    """
    Страница управления прикрепленными к порчению файлами
    """
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


class SaveReportMixin:
    url_name = 'reports'

    def save_report(self, report):
        try:
            report.save()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse(self.url_name) + f'?report={report.pk}'
            }))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportsCreateView(View, SaveReportMixin):
    """
    Страница добавления шаблона отчета
    """

    def post(self, request):

        report = ReportParams(
            name=request.POST.get('report_name'),
            order_fields=request.POST.getlist('order_fields'),
            transit_fields=request.POST.getlist('transit_fields'),
            ext_order_fields=request.POST.getlist('ext_order_fields'),
            segment_fields=request.POST.getlist('segment_fields'),
            user=request.user
        )

        return self.save_report(report)


class ReportUpdateView(View, SaveReportMixin):
    """
    Страница изменения шаблона отчета
    """

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        report.order_fields = request.POST.getlist('order_fields')
        report.transit_fields = request.POST.getlist('transit_fields')
        report.ext_order_fields = request.POST.getlist('ext_order_fields')
        report.segment_fields = request.POST.getlist('segment_fields')

        return self.save_report(report)


class ReportDeleteView(View):
    """
    Страница удаления шаблона отчета
    """
    url_name = 'reports'

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        try:
            report.delete()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse(self.url_name)
            }))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportsView(View, LoginRequiredMixin):
    """
    Страница генерации отчетов
    """
    template = 'management/reports.html'
    fields_form_class = ReportsForm
    filter_form_class = ReportsFilterForm
    generator_class = ReportGenerator
    filter_org_field = None
    filter_field = None
    login_url = 'login'

    def get(self, request):
        fields_form = self.fields_form_class()
        filter_form = self.filter_form_class()
        report_pk = request.GET.get('report')
        if report_pk:
            report = ReportParams.objects.filter(pk=report_pk)
            if report.exists():
                report = report.last()
                init_fields = [i for i in fields_form.fields if 'fields' in i]
                for field in init_fields:
                    fields_form.fields[field].initial = report.__getattribute__(field)
        else:
            fields_form.select_all()
        saved_reports = request.user.reports.all()
        return render(request, self.template, {
            'fields_form': fields_form, 'filter_form': filter_form, 'saved_reports': saved_reports
        })

    @staticmethod
    def create_csv(data, header):
        """
        Формирование CSV-файла
        :param data: данные для выведения в отчет
        :param header: заголовки таблицы с отчетом
        :return: HttpResponse  с файлом отчета
        """
        formatted_data = list()
        for row in data:
            formatted_row = list()
            for item in row:
                if isinstance(item, datetime.datetime):
                    formatted_row.append(item.strftime('%d/%m/%Y %H:%M:%S'))
                elif isinstance(item, datetime.date):
                    formatted_row.append(item.strftime('%d/%m/%Y'))
                elif isinstance(item, float):
                    if item > 1:
                        formatted_row.append(str(round(item, -2)).replace('.', ','))
                    else:
                        formatted_row.append(str(item).replace('.', ','))
                else:
                    formatted_row.append(item)
            formatted_data.append(formatted_row)

        file = StringIO()
        wr = csv.writer(file, delimiter=';')
        wr.writerow(header)
        wr.writerows(formatted_data)

        forbidden_chars = list()
        for char in file.getvalue():
            try:
                char.encode('cp1251')
            except UnicodeEncodeError as e:
                logger.error(e)
                forbidden_chars.append(char)

        result_text = file.getvalue()
        for char in forbidden_chars:
            result_text = result_text.replace(char, '?')

        response = HttpResponse(result_text.encode('cp1251'), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'
        return response

    @staticmethod
    def create_excel(data, header):
        """
        Формирование XLS-файла
        :param data: данные для выведения в отчет
        :param header: заголовки таблицы с отчетом
        :return: HttpResponse  с файлом отчета
        """
        with BytesIO() as b:
            excel = xlwt.Workbook(encoding='cp1251')
            sheet = excel.add_sheet('Report')
            style = xlwt.XFStyle()
            style.font.bold = True
            for column, item in enumerate(header):
                sheet.write(0, column, item, style)
            style = xlwt.XFStyle()
            for i, data_item in enumerate(data):
                for column, data in enumerate(data_item):
                    if isinstance(data, datetime.datetime):
                        style.num_format_str = 'DD/MM/YYYY hh:mm:ss'
                    elif isinstance(data, datetime.date):
                        style.num_format_str = 'DD/MM/YYYY'
                    elif isinstance(data, float):
                        style.num_format_str = '#,##0.00'
                    else:
                        style.num_format_str = 'General'
                    sheet.write(i + 1, column, data, style)
            excel.save(b)
            response = HttpResponse(b.getvalue(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=report.xls'
        return response

    def post(self, request):
        saved_reports = request.user.reports.all()
        fields_form = self.fields_form_class(data=request.POST)
        filter_form = self.filter_form_class(data=request.POST)
        if fields_form.is_valid():
            field_labels = list()
            init_fields = [i for i in fields_form.fields if 'fields' in i]
            for field in init_fields:
                field_labels += fields_form.cleaned_data.get(field)

            filters = filter_form.serialized_result()
            if self.filter_field is not None and self.filter_org_field is not None:
                filters[self.filter_field] = request.user._wrapped.__getattribute__(self.filter_org_field)

            generator = self.generator_class(field_labels, **filters)

            fields_verbose = generator.fields_verbose()
            objects = generator.serialize()
            if fields_form.cleaned_data.get('report_type') == 'csv':
                return self.create_csv(objects, fields_verbose)
            if fields_form.cleaned_data.get('report_type') == 'xlsx':
                return self.create_excel(objects, fields_verbose)
            return render(request, self.template, {
                'fields_form': fields_form, 'filter_form': filter_form, 'objects': objects, 'fields': fields_verbose,
                'saved_reports': saved_reports
            })

        return render(request, self.template, {
            'fields_form': fields_form, 'filter_form': filter_form, 'saved_reports': saved_reports
        })


def cargos_spreadsheet(request):
    """
    Форма копирования грузов из таблицы Excel
    """
    allowed_packages = ', '.join([i[1] for i in Cargo.package_type.field.choices])
    return render(request, 'management/cargos_spreadsheet.html', {'allowed_packages': allowed_packages})


class BaseBillOutputView(View):
    filter_form_class = BillOutputForm
    search_form_class = BillOutputSearchForm
    fields = None
    template_name = None
    sub_query_name = None
    bill_field_name = None

    @staticmethod
    def get_field(obj, field_name: str):
        value = obj

        for chunk in field_name.split('__'):
            value = value.__getattribute__(chunk)
            if callable(value):
                value = value()

        if isinstance(value, uuid.UUID) or isinstance(value, models.Model):
            return str(value)
        elif isinstance(value, datetime.date):
            return value.strftime('%d.%m.%Y')
        elif value is None:
            return ''
        return value

    def serialize_obj(self, obj):
        return [self.get_field(obj, field_name) for field_name in dict(self.fields)]

    def get_headers(self):
        return list(dict(self.fields).values())

    def get_sub_queryset(self, obj, no_bill: bool = False, search: str = None):
        sub_query_base = obj.__getattribute__(self.sub_query_name)
        if search:
            bill_field__icontains = f'{self.bill_field_name}__icontains'
            return sub_query_base.filter(**{bill_field__icontains: search})
        if no_bill:
            bill_field__isnull = f'{self.bill_field_name}__isnull'
            return sub_query_base.filter(**{bill_field__isnull: True})
        return sub_query_base.all()

    def get_search_queryset(self, search: str):
        sub_model = Order().__getattribute__(self.sub_query_name).model
        return sub_model.objects.filter(**{f'{self.bill_field_name}__icontains': search})

    def post(self, request):
        filter_form = self.filter_form_class(request.POST)
        search_form = self.search_form_class(request.POST)
        if filter_form.is_valid():
            queryset = Order.objects.filter(
                client=filter_form.cleaned_data['client'],
                type=filter_form.cleaned_data['type'],
                to_date_fact__gte=filter_form.cleaned_data['delivered_from'],
                to_date_fact__lte=filter_form.cleaned_data['delivered_to'],
                re_submission=False
            )
            post_data = list()
            for obj in queryset:
                sub_queryset = self.get_sub_queryset(obj, filter_form.cleaned_data['empty_only'])
                for sub_obj in sub_queryset:
                    post_data.append(self.serialize_obj(sub_obj))
            return HttpResponse(json.dumps({'headers': self.get_headers(), 'data': post_data}))
        elif search_form.is_valid():
            queryset = self.get_search_queryset(search_form.cleaned_data['search'])
            post_data = [self.serialize_obj(sub_obj) for sub_obj in queryset]
            return HttpResponse(json.dumps({'headers': self.get_headers(), 'data': post_data}))
        return render(request, self.template_name, {'filter_form': filter_form, 'search_form': search_form})


class BillOutputView(View):
    """
    Страница предпросмотра детализации
    """
    def get(self, request):
        filter_form = BillOutputForm()
        search_form = BillOutputSearchForm()
        return render(request, 'management/bill_output.html', {'filter_form': filter_form, 'search_form': search_form})


class InternalBillData(BaseBillOutputView):
    sub_query_name = 'transits'
    bill_field_name = 'bill_number'
    fields = (
        ('pk', 'id'),
        ('order__client_number', '№ поручения'),
        ('order__manager', 'Менеджер'),
        ('order__client_employee', 'Наблюдатель'),
        ('number', '№ маршрута'),
        ('to_date_fact', 'Дата доставки'),
        ('weight_payed', 'Опл. вес, кг'),
        ('get_status_display', 'Статус доставки'),
        ('price', 'Ставка'),
        ('get_price_currency_display', 'Валюта'),
        ('order__get_taxes_display', 'НДС'),
        ('order__contract__number', '№ договора'),
        ('bill_number', '№ счета'),
    )


class InternationalBillData(BaseBillOutputView):
    sub_query_name = 'ext_orders'
    bill_field_name = 'bill_client'
    fields = (
        ('pk', 'id'),
        ('order__client_number', '№ поручения'),
        ('manager', 'Менеджер'),
        ('contractor_employee', 'Сотрудник подрядчика'),
        ('number', '№ исходящего поручения'),
        ('to_date_fact', 'Дата доставки'),
        ('weight_payed', 'Опл. вес, кг'),
        ('get_status_display', 'Статус доставки'),
        ('price_client', 'Ставка'),
        ('get_currency_client_display', 'Валюта'),
        ('order__get_taxes_display', 'НДС'),
        ('order__contract__number', '№ договора'),
        ('bill_client', '№ счета'),
    )


class BillOutputPostView(View):
    """
    Сохранение данных из таблицы предпросмотра детализации
    """
    order_type = None
    model = None

    def post(self, request):
        data = json.loads(request.POST.get('data'))
        bill_data = dict()

        for item in data:
            trans_pk = item[0]
            bill_number = item[-1] if item[-1] != 'null' else None
            if bill_number not in bill_data:
                bill_data[bill_number] = list()
            bill_data[bill_number].append(trans_pk)

        cookie_name = f'{self.order_type}_bill'

        request.session[cookie_name] = dict()

        request.session[cookie_name]['bill_data'] = bill_data
        request.session[cookie_name]['period'] = (request.POST.get('delivered_from'), request.POST.get('delivered_to'))

        if request.POST.get('client'):
            client_pk = request.POST.get('client')
            client = Client.objects.get(pk=client_pk)
            filename = 'Детализация {} {}.pdf'.format(
                client.short_name.replace('"', ''),
                timezone.now().strftime("%d.%m.%Y")
            )

        else:
            any_order_pk = list(bill_data.values())[-1][-1]
            if any_order_pk:
                any_obj = self.model.objects.get(pk=any_order_pk)
                client = any_obj.order.client
                filename = 'Детализация {} {}.pdf'.format(
                    client.short_name.replace('"', ''),
                    timezone.now().strftime("%d.%m.%Y")
                )
            else:
                filename = 'Детализация {}.pdf'.format(
                    timezone.now().strftime("%d.%m.%Y")
                )

        return HttpResponse(
            json.dumps({'uri': reverse(f'bills_blank_{self.order_type}', kwargs={'filename': filename})})
        )


class InternalBillOutputPostView(BillOutputPostView):
    order_type = 'internal'
    model = Transit


class InternationalBillOutputPostView(BillOutputPostView):
    order_type = 'international'
    model = ExtOrder


class ExtOrderListView(LoginRequiredMixin, FilteredListView):
    """
    Страница "Поручения"
    """
    login_url = 'login'
    model = ExtOrder
    form_class = ExtOrderListFilters1
    template_name = 'management/extorder_list.html'
    paginate_by = 10
    search_fields = ['number']
    filter_fields = ['contractor', 'manager', 'status']
    filter_optional = ['contractor']

    def get_form(self, form_class=None):
        """
        Генератор списка пользователей для фильтра
        """
        form = super(ExtOrderListView, self).get_form(form_class)
        qs_contractor = form.fields['contractor'].queryset
        qs_manager = form.fields['manager'].queryset
        qs_contractor = qs_contractor.order_by('short_name')
        qs_manager = qs_manager.order_by('last_name', 'first_name')
        form.fields['contractor'].queryset = qs_contractor
        form.fields['manager'].queryset = qs_manager
        return form

    def form_valid(self, form):
        """
        Проверка валидности фильтра
        """
        force_empty = {}
        for fn in self.filter_optional:
            if form.cleaned_data.get(fn) == 'none':
                form.cleaned_data.pop(fn)
                force_empty[fn] = None
        queryset = super(ExtOrderListView, self).form_valid(form)
        queryset = queryset.filter(**force_empty)
        for fn in force_empty:
            form.cleaned_data[fn] = 'none'

        if form.cleaned_data['from_date']:
            queryset = queryset.filter(created_at__gte=form.cleaned_data['from_date'])
        if form.cleaned_data['to_date']:
            queryset = queryset.filter(created_at__lte=form.cleaned_data['to_date'])
        return queryset


class ExtOrderDetailView(LoginRequiredMixin, DetailView):
    """
    Детализация исходящего поручения
    """
    login_url = 'login'
    model = ExtOrder
    template_name = 'management/extorder_detail.html'
