import uuid

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from app_auth.mailer import send_technical_mail
from app_auth.models import Organisation, User
from configs.groups_perms import get_or_init, ORG_USER, ORG_ADMIN, STAFF_USER
from management.forms import UserAddForm, UserEditForm


class UserIsStaffMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff


def dashboard(request):
    return render(request, 'management/dashboard.html', {})


class OrgListView(UserIsStaffMixin, ListView):
    login_url = 'login'
    model = Organisation
    template_name = 'management/orgs_list.html'


class OrgDetailView(UserIsStaffMixin, DetailView):
    login_url = 'login'
    model = Organisation
    template_name = 'management/orgs_detail.html'


class OrgAddView(UserIsStaffMixin, CreateView):
    login_url = 'login'
    model = Organisation
    fields = '__all__'
    template_name = 'management/orgs_add.html'

    def get_success_url(self):
        return reverse('orgs_detail', kwargs={'pk': self.object.pk})


class OrgEditView(UserIsStaffMixin, UpdateView):
    login_url = 'login'
    model = Organisation
    fields = '__all__'
    template_name = 'management/orgs_edit.html'

    def get_success_url(self):
        return reverse('orgs_detail', kwargs={'pk': self.object.pk})


class OrgDeleteView(UserIsStaffMixin, DeleteView):
    login_url = 'login'
    model = Organisation
    template_name = 'management/orgs_delete.html'

    def get_success_url(self):
        return reverse('orgs_list')


class UserListView(UserIsStaffMixin, ListView):
    login_url = 'login'
    model = User
    template_name = 'management/user_list.html'


class UserDetailView(UserIsStaffMixin, DetailView):
    login_url = 'login'
    model = User
    template_name = 'management/user_detail.html'


class UserAddView(UserIsStaffMixin, View):
    login_url = 'login'

    def get(self, request):
        form = UserAddForm()
        form.fields['is_org_admin'].initial = False
        if request.GET.get('org'):
            orgs = Organisation.objects.filter(id=request.GET.get('org'))
            if orgs.exists():
                org = orgs.last()
                form.fields['org'].initial = org
        return render(request, 'management/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(uuid.uuid4().hex)
            user.username = uuid.uuid4().hex
            user.groups.add(get_or_init('ORG_USER', ORG_USER))
            if request.user.is_staff and user.is_org_admin:
                user.groups.add(get_or_init('ORG_ADMIN', ORG_ADMIN))
            if request.user.is_staff and user.is_staff:
                user.groups.add(get_or_init('ORG_ADMIN', ORG_ADMIN))
                user.groups.add(get_or_init('STAFF_USER', STAFF_USER))
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


class UserEditView(UserIsStaffMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(instance=user)
        return render(request, 'management/user_edit.html', {'form': form})

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            if user.is_staff:
                user.groups.add(get_or_init('STAFF_USER', STAFF_USER))
                user.is_org_admin = True
            else:
                group = get_or_init('STAFF_USER', STAFF_USER)
                group.user_set.remove(user)

            if user.is_org_admin:
                user.groups.add(get_or_init('ORG_ADMIN', ORG_ADMIN))
            else:
                group = get_or_init('ORG_ADMIN', ORG_ADMIN)
                group.user_set.remove(user)

            form.save()
            return redirect(request.GET['next'])
        return render(request, 'management/user_edit.html', {'form': form})


class UserDeleteView(UserIsStaffMixin, DeleteView):
    login_url = 'login'
    model = User
    template_name = 'management/user_delete.html'

    def get_success_url(self):
        return reverse('users_list')
