import csv
import datetime
import json
import logging
import uuid
from io import StringIO, BytesIO

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.forms import DateInput, CheckboxSelectMultiple
from django.forms.models import ModelChoiceIterator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.forms import AuditorForm, ContractorContractForm
from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client, Contractor, Auditor, ReportParams, ContractorContract
from configs.groups_perms import get_or_init
from management.forms import UserAddForm, UserEditForm, OrderEditTransitFormset, OrderCreateTransitFormset, \
    OrderListFilters, ReportsForm, ReportsFilterForm, BillOutputForm, ExtOrderListFilters1
from management.reports import ReportGenerator
from orders.forms import OrderStatusFormset, TransitStatusFormset, OrderForm, FileUploadFormset, ExtOrderFormset
from orders.mailer import order_assigned_to_manager, order_assigned_to_manager_for_client, \
    extorder_assigned_to_carrier_for_carrier
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

    def get(self, request, pk):
        contractor = Contractor.objects.get(pk=pk)
        form = ContractorContractForm()
        return render(request, 'management/contract_add_full.html', {'form': form, 'contractor': contractor})

    def post(self, request, pk):
        contractor = Contractor.objects.get(pk=pk)
        form = ContractorContractForm(request.POST)
        if form.is_valid():
            obj = form.save(False)
            obj.contractor = contractor
            obj.update_current_sum()
            return redirect('contractor_detail', pk=contractor.pk)
        return render(request, 'management/contract_add_full.html', {'form': form, 'contractor': contractor})


class ContractorContractEditFullView(UpdateView):
    template_name = 'management/contract_edit_full.html'
    model = ContractorContract
    form_class = ContractorContractForm

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

    def test_func(self):
        return self.request.user == self.object.manager

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user != order.manager:
            return redirect('order_detail', pk=pk)
        order_form = OrderForm(instance=order)
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client).order_by('last_name',
                                                                                                          'first_name')
        order_form.fields['manager'].queryset = User.objects.filter(client=None).order_by('last_name', 'first_name')
        transits = OrderEditTransitFormset(instance=order)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'order': order, 'transits': transits})

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user != order.manager:
            return redirect('order_detail', pk=pk)
        data = request.POST.copy()
        if order.created_by:
            data['created_by'] = order.created_by.pk
        order_form = OrderForm(data, instance=order)
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client).order_by('last_name',
                                                                                                          'first_name')
        transits = OrderEditTransitFormset(data, instance=order)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save()
            if 'manager' in order_form.changed_data and order_form.cleaned_data.get('manager') is not None:
                order_assigned_to_manager(request, order)
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            else:
                order.enumerate_transits()
            return redirect('order_detail', pk=pk)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'order': order, 'transits': transits})


class OrderCreateView(PermissionRequiredMixin, View):
    """
    Страница добавления нового поручения
    """
    permission_required = ['orders.add_order', 'orders.view_all_orders']
    login_url = 'login'

    def get(self, request):
        order_form = OrderForm()
        order_form.fields['client_employee'].queryset = User.objects.none()
        transits = OrderCreateTransitFormset()
        return render(request, 'management/order_add.html',
                      {'order_form': order_form, 'transits': transits})

    def post(self, request):
        data = request.POST.copy()
        data['created_by'] = request.user.pk
        order_form = OrderForm(data)
        order_form.fields['client_employee'].queryset = User.objects.none()
        transits = OrderCreateTransitFormset(data)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save()
            transits.instance = order
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list')
            else:
                order.enumerate_transits()
            return redirect('order_detail', pk=order.pk)
        return render(request, 'management/order_add.html',
                      {'order_form': order_form, 'transits': transits})


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
                                                 'to_addr': transit.to_addr,
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
            # Подготовка к пересчету
            tempvar2 = len(transit.ext_orders.all())
            tempvar = []
            if tempvar2 > 0:
                # Если у нас исходящих поручений больше, чем 0 то у нас заполняется временная переменная с id
                # перевозчиков
                for i in transit.ext_orders.all().order_by('created_at'):
                    # здесь не желательно что то менять - необходимо сравнивать былую структуру с новой.
                    tempvar.append(i.contractor.id) if i.contractor is not None else tempvar.append(None)
            ext_orders_formset.save()
            transit.enumerate_ext_orders()
            transit2 = Transit.objects.get(pk=pk)
            qs_extorders_in_transit2 = transit2.ext_orders.only('contractor', 'created_at').order_by('created_at')
            if tempvar2 > 0:
                # Если хотябы одно поручение было до проверки...
                if len(qs_extorders_in_transit2) > tempvar2:
                    # Если количество поручений превышает былое количество то отправляем всем тем, кто добавился
                    for i in range(tempvar2, len(qs_extorders_in_transit2)):
                        #костыль для хот-фикса
                        if qs_extorders_in_transit2[i].contractor is not None:
                            extorder_assigned_to_carrier_for_carrier(request, qs_extorders_in_transit2[i])
                # Затем проверяем тех, кто был до этого
                for enum, i in enumerate(tempvar):
                    # Костыль, дабы не было 5хх при снижении количества поручений
                    if len(qs_extorders_in_transit2) > enum:
                        # Если перевозчик сменился, то отправляем новому уведомление
                        # Проверка первостепенна, иначе будет 5хх
                        if qs_extorders_in_transit2[enum].contractor is not None:
                            if qs_extorders_in_transit2[enum].contractor.id != i:
                                extorder_assigned_to_carrier_for_carrier(request, qs_extorders_in_transit2[enum])
            else:
                # Если в начале не было поручений, то шлем всем уведомления
                for i in qs_extorders_in_transit2:
                    if i.contractor is not None:
                        extorder_assigned_to_carrier_for_carrier(request, i)
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


class ReportsCreateView(View):
    """
    Страница добавления шаблона отчета
    """

    def post(self, request):
        if request.POST.get('merge_segments') == 'on':
            merge = True
        else:
            merge = False
        report = ReportParams(
            name=request.POST.get('report_name'),
            order_fields=request.POST.getlist('order_fields'),
            transit_fields=request.POST.getlist('transit_fields'),
            ext_order_fields=request.POST.getlist('ext_order_fields'),
            segment_fields=request.POST.getlist('segment_fields'),
            user=request.user
        )

        try:
            report.save()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports') + f'?report={report.pk}'
            }))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportUpdateView(View):
    """
    Страница изменения шаблона отчета
    """

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        report.order_fields = request.POST.getlist('order_fields')
        report.transit_fields = request.POST.getlist('transit_fields')
        report.ext_order_fields = request.POST.getlist('ext_order_fields')
        report.segment_fields = request.POST.getlist('segment_fields')

        try:
            report.save()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports') + f'?report={report.pk}'
            }))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportDeleteView(View):
    """
    Страница удаления шаблона отчета
    """

    def post(self, request, report_id):
        report = ReportParams.objects.get(pk=report_id)
        try:
            report.delete()
            return HttpResponse(json.dumps({
                'status': 'ok',
                'url': reverse('reports')
            }))
        except Exception as e:
            logger.error(e)
            return HttpResponse(json.dumps({
                'status': 'error',
                'message': e
            }))


class ReportsView(View):
    """
    Страница генерации отчетов
    """

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
                fields_form.fields['ext_order_fields'].initial = report.ext_order_fields
                fields_form.fields['segment_fields'].initial = report.segment_fields
        else:
            fields_form.select_all()
        saved_reports = request.user.reports.all()
        return render(request, 'management/reports.html', {
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
        fields_form = ReportsForm(data=request.POST)
        filter_form = ReportsFilterForm(data=request.POST)
        if fields_form.is_valid():
            order_fields = fields_form.cleaned_data.get('order_fields')
            transit_fields = fields_form.cleaned_data.get('transit_fields')
            ext_order_fields = fields_form.cleaned_data.get('ext_order_fields')
            segment_fields = fields_form.cleaned_data.get('segment_fields')

            # filter_form.full_clean()
            generator = ReportGenerator(
                order_fields + transit_fields + ext_order_fields + segment_fields,
                **filter_form.serialized_result()
            )

            fields_verbose = generator.fields_verbose()
            objects = generator.serialize()
            if fields_form.cleaned_data.get('report_type') == 'csv':
                return self.create_csv(objects, fields_verbose)
            if fields_form.cleaned_data.get('report_type') == 'xlsx':
                return self.create_excel(objects, fields_verbose)
            return render(request, 'management/reports.html', {
                'fields_form': fields_form, 'filter_form': filter_form, 'objects': objects, 'fields': fields_verbose,
                'saved_reports': saved_reports
            })

        return render(request, 'management/reports.html', {
            'fields_form': fields_form, 'filter_form': filter_form, 'saved_reports': saved_reports
        })


def cargos_spreadsheet(request):
    """
    Форма копирования грузов из таблицы Excel
    """
    allowed_packages = ', '.join([i[1] for i in Cargo.package_type.field.choices])
    return render(request, 'management/cargos_spreadsheet.html', {'allowed_packages': allowed_packages})


class BillOutputView(View):
    """
    Страница предпросмотра детализации
    """

    def get(self, request):
        form = BillOutputForm()
        return render(request, 'management/bill_output.html', {'form': form})

    def post(self, request):
        form = BillOutputForm(request.POST)
        if form.is_valid():
            queryset = Order.objects.filter(
                client=form.cleaned_data['client'],
                to_date_fact__gte=form.cleaned_data['delivered_from'],
                to_date_fact__lte=form.cleaned_data['delivered_to'],
            )
            post_data = list()
            for order in queryset:
                if form.cleaned_data['empty_only']:
                    transits = order.transits.filter(bill_number__isnull=True)
                else:
                    transits = order.transits.all()
                for transit in transits:
                    post_data.append([
                        str(transit.pk),
                        order.client_number,
                        transit.number,
                        transit.to_date_fact.strftime('%d.%m.%Y'),
                        transit.weight_payed,
                        transit.get_status_display(),
                        transit.price,
                        transit.get_price_currency_display(),
                        order.get_taxes_display(),
                        order.contract.number,
                        transit.bill_number,
                    ])
            return HttpResponse(json.dumps(post_data))
        return render(request, 'management/bill_output.html', {'form': form})


class BillOutputPostView(View):
    """
    Сохранение данных из таблицы предпросмотра детализации
    """

    def post(self, request):
        data = json.loads(request.POST.get('data'))
        bill_data = dict()

        for item in data:
            trans_pk = item[0]
            bill_number = item[-1] if item[-1] != 'null' else None
            if bill_number not in bill_data:
                bill_data[bill_number] = list()
            bill_data[bill_number].append(trans_pk)

        request.session['bill_data'] = bill_data
        request.session['period'] = (request.POST.get('delivered_from'), request.POST.get('delivered_to'))
        client = Client.objects.get(pk=request.POST.get('client'))
        filename = 'Детализация {} {}.pdf'.format(
            client.short_name.replace('"', ''),
            timezone.now().strftime("%d.%m.%Y")
        )
        return HttpResponse(json.dumps({'uri': reverse('bills_blank', kwargs={'filename': filename})}))


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
    default_order = '-date'

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
