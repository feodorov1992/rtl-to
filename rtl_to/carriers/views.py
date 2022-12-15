import uuid

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import User
from carriers.forms import UserAddForm, UserEditForm
from configs.groups_perms import get_or_init


def dashboard(request):
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
    login_url = 'login'
    model = User
    template_name = 'carriers/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(contractor=self.request.user.contractor)


class UserDetailView(DetailView):
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


class OrderListView(ListView):
    pass


class OrderDetailView(DetailView):
    pass


class OrderHistoryView(View):
    pass


class OrderEditView(View):
    pass
