import uuid

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import Organisation, User
from configs.groups_perms import get_or_init, ORG_USER, ORG_ADMIN, STAFF_USER
from clientsarea.forms import UserAddForm, UserEditForm


class UserIsOrgAdminMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_org_admin


def dashboard(request):
    return render(request, 'clientsarea/dashboard.html', {})


class UserListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_list.html'

    def get_queryset(self):
        return self.model.objects.filter(org=self.request.user.org)


class UserDetailView(DetailView):
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_detail.html'

    def get_object(self, queryset=None):
        user = super(UserDetailView, self).get_object()
        if self.request.user.org == user.org:
            return user
        else:
            raise PermissionError


class UserAddView(UserIsOrgAdminMixin, View):
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
            user.groups.add(get_or_init('ORG_USER', ORG_USER))
            user.is_active = False
            user.save()
            send_technical_mail(
                request, user,
                subject='Подтверждение регистрации',
                from_email='d.fedorov@rtl-to.ru',
                link_name='registration_confirm',
                mail_template='app_auth/mail/acc_active_email.html'
            )
            return redirect('users_list_pub')
        return render(request, 'clientsarea/user_add.html', {'form': form})


class UserEditView(UserIsOrgAdminMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.org != user.org:
            raise PermissionError
        form = UserEditForm(instance=user)
        return render(request, 'clientsarea/user_edit.html', {'form': form, 'user': user})

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.org != user.org:
            raise PermissionError
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(request.GET['next'])
        return render(request, 'clientsarea/user_edit.html', {'form': form, 'user': user})


class UserDeleteView(UserIsOrgAdminMixin, DeleteView):
    login_url = 'login'
    model = User
    template_name = 'clientsarea/user_delete.html'

    def get_success_url(self):
        return reverse('users_list')

    def get_object(self, queryset=None):
        user = super(UserDeleteView, self).get_object()
        if self.request.user.org == user.org:
            return user
        else:
            raise PermissionError
