import datetime
import logging
import uuid

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.mailer import send_technical_mail
from app_auth.models import User
from configs.groups_perms import get_or_init
from clientsarea.forms import UserAddForm, UserEditForm, OrderCreateTransitFormset, FileUploadFormset, OrderListFilters
from orders.forms import OrderForm
from orders.models import Order, Cargo

logger = logging.getLogger(__name__)


def dashboard(request):
    """
    Страница "Общая информация"
    """
    all_orders = request.user.client.orders.all()
    active_orders = all_orders.exclude(status__in=['completed', 'rejected'])
    late_orders = active_orders.filter(to_date_plan__lt=datetime.date.today())

    all_users = request.user.client.users.all()
    active_users = all_users.filter(is_active=True)

    return render(request, 'clientsarea/dashboard.html', {
        'all_orders': all_orders.count(),
        'active_orders': active_orders.count(),
        'late_orders': late_orders.count(),
        'all_users': all_users.count(),
        'active_users': active_users.count()
    })


class UserListView(LoginRequiredMixin, ListView):
    """
    Страница "Коллеги"
    """
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(client=self.request.user.client)


class UserDetailView(DetailView):
    """
    Детализация по пользователю
    """
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_detail.html'

    def get_object(self, queryset=None):
        user = super(UserDetailView, self).get_object()
        if self.request.user.client == user.client:
            return user
        else:
            raise PermissionError


class UserAddView(PermissionRequiredMixin, View):
    """
    Страница добавления пользователя
    """
    permission_required = 'app_auth.add_user'
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        return render(request, 'clientsarea/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.client = request.user.client
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.user_type = 'client_simple'
            user.groups.add(get_or_init('client_simple'))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('users_list_pub')
        return render(request, 'clientsarea/user_add.html', {'form': form})


class UserEditView(PermissionRequiredMixin, UpdateView):
    """
    Страница редактирования пользователя
    """
    permission_required = 'app_auth.change_user'
    template_name = 'clientsarea/user_edit.html'
    form_class = UserEditForm
    model = User

    def get_success_url(self):
        return self.request.GET['next']

    def get_object(self, queryset=None):
        user = super(UserEditView, self).get_object()
        if self.request.user.client == user.client:
            return user
        else:
            raise PermissionError


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Страница удаления пользователя
    """
    permission_required = 'app_auth.delete_user'
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_delete.html'

    def get_success_url(self):
        return reverse('users_list_pub')

    def get_object(self, queryset=None):
        user = super(UserDeleteView, self).get_object()
        if self.request.user.client == user.client:
            return user
        else:
            raise PermissionError


class OrderListView(LoginRequiredMixin, FilteredListView):
    """
    Страница "Поручения"
    """
    login_url = 'login'
    model = Order
    form_class = OrderListFilters
    template_name = 'clientsarea/order_list.html'
    paginate_by = 10

    search_fields = ['inner_number', 'client_number']
    filter_fields = ['type', 'client_employee', 'status']
    filter_optional = ['client_employee']
    default_order = '-order_date'

    def get_form(self, form_class=None):
        """
        Генератор списка пользователей для фильтра
        """
        form = super(OrderListView, self).get_form(form_class)
        _qs = form.fields['client_employee'].queryset
        _qs = _qs.filter(client=self.request.user.client).order_by('last_name', 'first_name')
        form.fields['client_employee'].queryset = _qs
        return form

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(client=self.request.user.client)

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
        """
        Проверка валидности фильтра
        """
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
    """
    Детализация поручения
    """
    login_url = 'login'
    model = Order
    template_name = 'clientsarea/order_detail.html'

    def get_object(self, queryset=None):
        order = super(OrderDetailView, self).get_object(queryset)
        if order.client == self.request.user.client:
            return order
        else:
            raise PermissionError


class OrderHistoryView(LoginRequiredMixin, DetailView):
    """
    Страница истории поручения
    """
    login_url = 'login'
    model = Order
    template_name = 'clientsarea/order_history.html'

    def get_object(self, queryset=None):
        order = super(OrderHistoryView, self).get_object(queryset)
        if order.client == self.request.user.client:
            return order
        else:
            raise PermissionError


class OrderCreateView(PermissionRequiredMixin, View):
    """
    Страница добавления поручения
    """
    permission_required = 'orders.add_order'
    login_url = 'login'

    def get(self, request):
        order_form = OrderForm()
        transits = OrderCreateTransitFormset()
        return render(request, 'clientsarea/order_add.html',
                      {'order_form': order_form, 'transits': transits})

    def post(self, request):
        data = request.POST.copy()
        data['client'] = request.user.client.pk
        data['client_employee'] = request.user.pk
        data['created_by'] = request.user.pk
        data['status'] = 'new'
        data['insurance_premium_coeff'] = 0.00055
        order_form = OrderForm(data)
        transits = OrderCreateTransitFormset(data)
        if transits.is_valid() and order_form.is_valid():
            order = order_form.save()
            transits.instance = order
            transits.save()
            if not order.transits.exists():
                order.delete()
                return redirect('orders_list_pub')
            else:
                order.enumerate_transits()
            return redirect('order_detail_pub', pk=order.pk)
        logger.error(order_form.errors)
        logger.error(transits.errors)
        return render(request, 'clientsarea/order_add.html',
                      {'order_form': order_form, 'transits': transits})


class OrderFileUpload(View):
    """
    Страница прикрепления файла
    """
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user.client == order.client:
            docs_formset = FileUploadFormset(instance=order)
            return render(request, 'clientsarea/docs_list_edit.html', {'docs_formset': docs_formset})
        else:
            raise PermissionError

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user.client == order.client:
            docs_formset = FileUploadFormset(request.POST, request.FILES, instance=order)
            if docs_formset.is_valid():
                docs = docs_formset.save(commit=False)
                if docs:
                    for doc in docs:
                        doc.public = True
                        doc.save()
                else:
                    docs_formset.save()
                return redirect('order_detail_pub', pk=pk)
            return render(request, 'clientsarea/docs_list_edit.html', {'docs_formset': docs_formset})
        else:
            raise PermissionError


class CustomerGetOrderView(View):
    """
    Кнопка "Взять в работу"
    """

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user.client == order.client:
            order.client_employee = request.user
            order.save()
            return redirect(request.GET.get('next', 'orders_list_pub'))
        else:
            raise PermissionError


class CancelOrderView(View):
    """
    Кнопка "Аннулировать"
    """
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user.client == order.client:
            order.status = 'rejected'
            order.save()
            return redirect(request.GET.get('next', 'orders_list_pub'))
        else:
            raise PermissionError


def cargos_spreadsheet(request):
    allowed_packages = ', '.join([i[1] for i in Cargo.package_type.field.choices])
    return render(request, 'clientsarea/cargos_spreadsheet.html', {'allowed_packages': allowed_packages})
