import uuid

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django_genericfilters.views import FilteredListView

from app_auth.mailer import send_technical_mail
from app_auth.models import User
from carriers.forms import UserAddForm, UserEditForm, OrderListFilters, ExtOrderEditForm, CarrierExtOrderForm
from configs.groups_perms import get_or_init
from orders.forms import ExtOrderSegmentFormset
from orders.models import ExtOrder
from print_forms.views import return_url


def dashboard(request):
    """
    Страница "Общая информация"
    """
    if request.user.contractor:
        # all_orders = request.user.contractor.ext_orders.all()
        all_users = request.user.contractor.users.all()
    else:
        # all_orders = Order.objects.none()
        all_users = User.objects.none()
    # active_orders = all_orders.exclude(status__in=['completed', 'rejected'])
    # late_orders = active_orders.filter(to_date_plan__lt=datetime.date.today())
    active_users = all_users.filter(is_active=True)

    return render(request, 'carriers/dashboard.html', {
        # 'all_orders': all_orders.count(),
        # 'active_orders': active_orders.count(),
        # 'late_orders': late_orders.count(),
        'all_users': all_users.count(),
        'active_users': active_users.count()
    })


class UserListView(LoginRequiredMixin, ListView):
    """
    Страница "Коллеги"
    """
    login_url = 'login'
    model = User
    template_name = 'carriers/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(contractor=self.request.user.contractor)


class UserDetailView(DetailView):
    """
    Детализация по пользователю
    """
    login_url = 'login'
    model = User
    template_name = 'carriers/user_detail.html'

    def get_object(self, queryset=None):
        user = super(UserDetailView, self).get_object()
        if self.request.user.contractor == user.contractor:
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
        return render(request, 'carriers/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.contractor = request.user.contractor
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.user_type = 'contractor_simple'
            user.groups.add(get_or_init('contractor_simple'))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('users_list_carrier')
        return render(request, 'carriers/user_add.html', {'form': form})


class UserEditView(PermissionRequiredMixin, UpdateView):
    """
    Страница редактирования пользователя
    """
    permission_required = 'app_auth.change_user'
    template_name = 'carriers/user_edit.html'
    form_class = UserEditForm
    model = User

    def get_success_url(self):
        return self.request.GET['next']

    def get_object(self, queryset=None):
        user = super(UserEditView, self).get_object()
        if self.request.user.contractor == user.contractor:
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
    template_name = 'carriers/user_delete.html'

    def get_success_url(self):
        return reverse('users_list_carrier')

    def get_object(self, queryset=None):
        user = super(UserDeleteView, self).get_object()
        if self.request.user.contractor == user.contractor:
            return user
        else:
            raise PermissionError


class OrderListView(LoginRequiredMixin, FilteredListView):
    """
    Страница "Поручения"
    """
    login_url = 'login'
    model = ExtOrder
    form_class = OrderListFilters
    template_name = 'carriers/ext_order_list.html'
    paginate_by = 10
    search_fields = ['number']
    filter_fields = ['contractor_employee', 'status']
    filter_optional = ['contractor_employee']
    default_order = '-date'

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(contractor=self.request.user.contractor)

    def get_form(self, form_class=None):
        """
        Генератор списка пользователей для фильтра
        """
        form = super(OrderListView, self).get_form(form_class)
        _qs = form.fields['contractor_employee'].queryset
        _qs = _qs.filter(contractor=self.request.user.contractor).order_by('last_name', 'first_name')
        form.fields['contractor_employee'].queryset = _qs
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
        queryset = super(OrderListView, self).form_valid(form)
        queryset = queryset.filter(**force_empty)
        for fn in force_empty:
            form.cleaned_data[fn] = 'none'

        if form.cleaned_data['from_date']:
            queryset = queryset.filter(created_at__gte=form.cleaned_data['from_date'])
        if form.cleaned_data['to_date']:
            queryset = queryset.filter(created_at__lte=form.cleaned_data['to_date'])
        return queryset


class CarrierGetOrderView(View):
    """
    Кнопка "Взять в работу"
    """

    def get(self, request, pk):
        order = ExtOrder.objects.get(pk=pk)
        if request.user.contractor == order.contractor:
            order.contractor_employee = request.user
            order.save()
            return redirect(request.GET.get('next', 'orders_list_carrier'))
        else:
            raise PermissionError


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Детализация исходящего поручения
    """
    login_url = 'login'
    model = ExtOrder
    template_name = 'carriers/ext_order_detail.html'

    def get_object(self, queryset=None):
        order = super(OrderDetailView, self).get_object(queryset)
        if order.contractor == self.request.user.contractor:
            return order
        else:
            raise PermissionError


class OrderEditView(LoginRequiredMixin, UpdateView):
    """
    Страница редактирования поручения
    """
    login_url = 'login'
    model = ExtOrder
    form_class = ExtOrderEditForm
    template_name = 'carriers/price_edit.html'

    def get_object(self, queryset=None):
        order = super(OrderEditView, self).get_object(queryset)
        if order.contractor == self.request.user.contractor:
            return order
        else:
            raise PermissionError

    def get_success_url(self):
        return reverse('order_detail_carrier', kwargs={'pk': self.object.pk})


class SegmentsEditView(LoginRequiredMixin, View):
    """
    Страница управления плечами перевозки
    """
    login_url = 'login'

    def get(self, request, pk):
        order = ExtOrder.objects.get(pk=pk)
        ext_order_form = CarrierExtOrderForm(instance=order)
        segment_formset = ExtOrderSegmentFormset(instance=order, initials={
            'quantity': order.transit.quantity,
            'weight_payed': order.transit.weight,
            'weight_brut': order.transit.weight
        })
        ext_order_form.nested = segment_formset
        return render(request, 'carriers/order_segments.html',
                      {'segment_formset': segment_formset, 'ext_order_form': ext_order_form})

    def post(self, request, pk):
        order = ExtOrder.objects.get(pk=pk)
        ext_order_form = CarrierExtOrderForm(instance=order, data=request.POST)
        segment_formset = ExtOrderSegmentFormset(instance=order, data=request.POST)
        ext_order_form.nested = segment_formset
        if segment_formset.is_valid():
            segment_formset.save()
            return redirect('order_detail_carrier', pk=pk)
        return render(request, 'carriers/order_segments.html',
                      {'segment_formset': segment_formset, 'ext_order_form': ext_order_form})
