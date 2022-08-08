import datetime
import uuid

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.http import QueryDict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.mailer import send_technical_mail
from app_auth.models import User
from configs.groups_perms import get_or_init
from audit.forms import UserAddForm, UserEditForm, OrderListFilters
from orders.models import Order


def dashboard(request):
    if request.user.auditor:
        all_orders = request.user.auditor.orders.all()
        all_users = request.user.auditor.agents.all()
    else:
        all_orders = Order.objects.none()
        all_users = User.objects.none()
    active_orders = all_orders.exclude(status__in=['completed', 'rejected'])
    late_orders = active_orders.filter(to_date_plan__lt=datetime.date.today())
    active_users = all_users.filter(is_active=True)

    return render(request, 'audit/dashboard.html', {
        'all_orders': all_orders.count(),
        'active_orders': active_orders.count(),
        'late_orders': late_orders.count(),
        'all_users': all_users.count(),
        'active_users': active_users.count()
    })


class UserListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = User
    template_name = 'audit/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(auditor=self.request.user.auditor)


class UserDetailView(DetailView):
    login_url = 'login'
    model = User
    template_name = 'audit/user_detail.html'

    def get_object(self, queryset=None):
        user = super(UserDetailView, self).get_object()
        if self.request.user.auditor == user.auditor:
            return user
        else:
            raise PermissionError


class UserAddView(PermissionRequiredMixin, View):
    permission_required = 'app_auth.add_user'
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        return render(request, 'audit/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.auditor = request.user.auditor
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.user_type = 'auditor_simple'
            user.groups.add(get_or_init('auditor_simple'))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('users_list_aud')
        return render(request, 'audit/user_add.html', {'form': form})


class UserEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app_auth.change_user'
    template_name = 'audit/user_edit.html'
    form_class = UserEditForm
    model = User

    def get_success_url(self):
        return self.request.GET['next']

    def get_object(self, queryset=None):
        user = super(UserEditView, self).get_object()
        if self.request.user.auditor == user.auditor:
            return user
        else:
            raise PermissionError


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'app_auth.delete_user'
    login_url = 'login'
    model = User
    template_name = 'audit/user_delete.html'

    def get_success_url(self):
        return reverse('users_list_pub')

    def get_object(self, queryset=None):
        user = super(UserDeleteView, self).get_object()
        if self.request.user.auditor == user.auditor:
            return user
        else:
            raise PermissionError


class OrderListView(LoginRequiredMixin, FilteredListView):
    login_url = 'login'
    model = Order
    form_class = OrderListFilters
    template_name = 'audit/order_list.html'
    paginate_by = 10

    search_fields = ['inner_number', 'client_number']
    filter_fields = ['client', 'type', 'client_employee', 'status']
    filter_optional = ['client_employee']
    default_order = '-order_date'

    def get_form(self, form_class=None):
        form = super(OrderListView, self).get_form(form_class)

        _qs = form.fields['client_employee'].queryset
        _qs = _qs.filter(client__in=self.request.user.auditor.controlled_clients.all()).order_by('last_name',
                                                                                                 'first_name')
        form.fields['client_employee'].queryset = _qs
        form.fields['client'].queryset = self.request.user.auditor.controlled_clients.all()

        return form

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(auditors=self.request.user.auditor)

    def get_filters(self):
        filters = super(OrderListView, self).get_filters()
        for f in filters:
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


class OrderDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Order
    template_name = 'audit/order_detail.html'

    def get_object(self, queryset=None):
        order = super(OrderDetailView, self).get_object(queryset)
        if self.request.user.auditor in order.auditors.all():
            return order
        else:
            raise PermissionError


class OrderHistoryView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Order
    template_name = 'audit/order_history.html'

    def get_object(self, queryset=None):
        order = super(OrderHistoryView, self).get_object(queryset)
        if self.request.user.auditor in order.auditors.all():
            return order
        else:
            raise PermissionError
