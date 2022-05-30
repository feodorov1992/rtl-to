import datetime
import uuid

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client, Contractor
from configs.groups_perms import get_or_init
from management.forms import UserAddForm, UserEditForm, OrderEditTransitFormset, OrderCreateTransitFormset

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


class ClientDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'app_auth.view_all_clients'
    login_url = 'login'
    model = Client
    template_name = 'management/client_detail.html'


class ClientAddView(PermissionRequiredMixin, CreateView):
    permission_required = 'app_auth.add_client'
    login_url = 'login'
    model = Client
    fields = '__all__'
    template_name = 'management/client_add.html'

    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.pk})


class ClientEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app_auth.change_client'
    login_url = 'login'
    model = Client
    fields = '__all__'
    template_name = 'management/client_edit.html'

    def get_success_url(self):
        return reverse('client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'app_auth.delete_client'
    login_url = 'login'
    model = Client
    template_name = 'management/client_delete.html'

    def get_success_url(self):
        return reverse('clients_list')


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


class OrderListView(PermissionRequiredMixin, ListView):
    permission_required = 'orders.view_all_orders'
    login_url = 'login'
    model = Order
    template_name = 'management/order_list.html'


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ['orders.view_order', 'orders.view_all_orders']
    login_url = 'login'
    model = Order
    template_name = 'management/order_detail.html'


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
        order_form.fields['client_employee'].queryset = User.objects.filter(client=order.client)
        order_form.fields['manager'].queryset = User.objects.filter(client=None)
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
        return render(request, 'management/order_add.html',
                      {'order_form': order_form, 'transits': transits})


# class OrderCalcView(View):
#
#     def get(self, request):
#         calc_form = CalcForm()
#         cargos_formset = CargoCalcFormset()
#         return render(request, 'management/order_calc.html', {'calc_form': calc_form, 'cargos_formset': cargos_formset})
#
#     def post(self, request):
#         calc_form = CalcForm(request.POST)
#         cargos_formset = CargoCalcFormset(request.POST)
#         if calc_form.is_valid() and cargos_formset.is_valid():
#             print(cargos_formset.management_form.cleaned_data)
#             print(cargos_formset.cleaned_data)
#             # print(cargos_formset.forms)
#             # print(cargos_formset.cleaned_data)
#             cargos_formset.forms = [i for i in cargos_formset.forms if not i.cleaned_data.get('DELETE')]
#             cargos_formset.management_form.cleaned_data['TOTAL_FORMS'] = len(cargos_formset.forms)
#             print(cargos_formset.total_form_count())
#             # print(cargos_formset.forms)
#         return render(request, 'management/order_calc.html', {'calc_form': calc_form, 'cargos_formset': cargos_formset})


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
