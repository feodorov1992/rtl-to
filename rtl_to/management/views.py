import uuid

from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client
from configs.groups_perms import get_or_init
from management.forms import UserAddForm, UserEditForm, OrderForm, OrderEditTransitFormset, OrderCreateTransitFormset

from orders.forms import CalcForm, CargoCalcFormset, OrderStatusFormset, TransitStatusFormset
from orders.models import Order, OrderHistory, Transit, TransitHistory


def dashboard(request):
    return render(request, 'management/dashboard.html', {})


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
            user.groups.add(get_or_init(form.cleaned_data['user_type']))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                from_email='d.fedorov@rtl-to.ru',
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
            user.groups.add(get_or_init(form.cleaned_data['user_type']))
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


class OrderListView(ListView):
    model = Order
    template_name = 'management/order_list.html'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'management/order_detail.html'


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'management/order_delete.html'

    def get_success_url(self):
        return reverse('orders_list')


class OrderEditView(View):

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order_form = OrderForm(instance=order)
        transits = OrderEditTransitFormset(instance=order)
        # for transit in transits.forms:
        #     print(transit.fields['from_date_fact'].widget)
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
        print(order_form.errors)
        print(transits.errors)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'order': order, 'transits': transits})


class OrderCreateView(View):

    def get(self, request):
        order_form = OrderForm()
        transits = OrderCreateTransitFormset()
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'transits': transits})

    def post(self, request):
        order_form = OrderForm(request.POST)
        transits = OrderCreateTransitFormset(request.POST)
        if transits.is_valid() and order_form.is_valid():
            for n in transits.forms[0].nested:
                if n.is_valid():
                    print('cargo:', n.cleaned_data)
                else:
                    print(n.errors)
            # order = order_form.save()
            # transits.save()
            # if not order.transits.exists():
            #     order.delete()
            #     return redirect('orders_list')
            # return redirect('order_edit', pk=pk)
        return render(request, 'management/order_edit.html',
                      {'order_form': order_form, 'transits': transits})


class OrderCalcView(View):

    def get(self, request):
        calc_form = CalcForm()
        cargos_formset = CargoCalcFormset()
        return render(request, 'management/order_calc.html', {'calc_form': calc_form, 'cargos_formset': cargos_formset})

    def post(self, request):
        calc_form = CalcForm(request.POST)
        cargos_formset = CargoCalcFormset(request.POST)
        if calc_form.is_valid() and cargos_formset.is_valid():
            print(cargos_formset.management_form.cleaned_data)
            print(cargos_formset.cleaned_data)
            # print(cargos_formset.forms)
            # print(cargos_formset.cleaned_data)
            cargos_formset.forms = [i for i in cargos_formset.forms if not i.cleaned_data.get('DELETE')]
            cargos_formset.management_form.cleaned_data['TOTAL_FORMS'] = len(cargos_formset.forms)
            print(cargos_formset.total_form_count())
            # print(cargos_formset.forms)
        return render(request, 'management/order_calc.html', {'calc_form': calc_form, 'cargos_formset': cargos_formset})


class OrderHistoryEditView(View):

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


class TransitHistoryEditView(View):

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
