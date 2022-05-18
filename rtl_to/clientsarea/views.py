import uuid

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import Client, User
from configs.groups_perms import get_or_init
from clientsarea.forms import UserAddForm, UserEditForm


def dashboard(request):
    return render(request, 'clientsarea/dashboard.html', {})


class UserListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(client=self.request.user.client)


class UserDetailView(DetailView):
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
    permission_required = 'app_auth.add_user'
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        return render(request, 'clientsarea/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.groups.add(get_or_init('ORG_USER'))
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
