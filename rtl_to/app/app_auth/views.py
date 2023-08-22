import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views import View
from django.views.generic import UpdateView

from app_auth.forms import ProfileEditForm, CounterpartySelectForm, CounterpartyForm, ContactSelectForm, \
    ContactForm, ContractSelectForm, get_contract_form, ContractorContractForm, ClientContractForm
from app_auth.mailer import send_technical_mail
from app_auth.models import User, Client, Counterparty, Contact, Contractor, ContractorContract, ClientContract
from app_auth.tokens import TokenGenerator


def base_template(user: User):
    """
    Выбор базового шаблона общих страниц ЛК в зависимости от типа пользователя
    :param user: пользователь
    :return: путь и название базового шаблона
    """
    if hasattr(user, 'user_type'):
        if user.user_type == 'manager':
            return 'management/main_menu.html'
        elif user.user_type.startswith('client'):
            return 'clientsarea/main_menu.html'
        elif user.user_type.startswith('auditor'):
            return 'audit/main_menu.html'
        elif user.user_type.startswith('contractor'):
            return 'carriers/main_menu.html'
    return 'static_pages/base.html'


@login_required(login_url='login')
def profile_view(request):
    """
    Просмотр профиля пользователя
    """
    return render(request, 'app_auth/profile.html', {'base_tpl': base_template(request.user)})


def forgot_password_confirm(request):
    """
    Уведомление об отправке письма для восстановления забытого пароля
    """
    return render(request, 'app_auth/forgot_password_confirm.html', {})


class UserLoginView(LoginView):
    """
    Страница авторизации
    """
    template_name = 'app_auth/login.html'

    def get_form(self, form_class=None):
        form = super(UserLoginView, self).get_form(form_class)
        form.required_css_class = 'required'
        return form

    def get_success_url(self):
        """
        Выбор адреса для перенаправления после логина
        """
        if self.request.user.user_type == 'manager':
            return reverse('dashboard')
        else:
            if self.request.user.user_type.startswith('client'):
                return reverse('dashboard_pub')
            elif self.request.user.user_type.startswith('auditor'):
                return reverse('dashboard_aud')
            elif self.request.user.user_type.startswith('contractor'):
                return reverse('dashboard_carrier')


class UserLogoutView(LogoutView):
    """
    Выход из системы
    """
    @staticmethod
    def get_success_url():
        return reverse('home')


class ForgotPasswordView(View):
    """
    Страница восстановления забытого пароля
    """

    def get(self, request):
        form = PasswordResetForm()
        form.required_css_class = 'required'
        return render(request, 'app_auth/passwd_restore.html', {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        form.required_css_class = 'required'
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    send_technical_mail(
                        request, user,
                        subject='Восстановление пароля',
                        link_name='restore_password',
                        mail_template='app_auth/mail/password_reset_email.html'
                    )
                return redirect('forgot_password_confirm')
            form.add_error('email', 'Такого адреса нет в системе!')
        return render(request, 'app_auth/passwd_restore.html', {'form': form})


class PasswordRestoreView(View):
    """
    Страница ввода нового пароля взамен забытого
    """
    def get(self, request, pk, token):
        account_activation_token = TokenGenerator()
        user = User.objects.get(id=pk)
        if account_activation_token.check_token(user, token):
            form = SetPasswordForm(user=user)
            form.required_css_class = 'required'
            return render(request, 'app_auth/passwd_reset_form.html', {'form': form})
        return HttpResponse('Token is not valid. Please request the new one.')

    def post(self, request, pk, token):
        account_activation_token = TokenGenerator()
        user = User.objects.get(id=pk)
        if account_activation_token.check_token(user, token):
            form = SetPasswordForm(data=request.POST, user=user)
            form.required_css_class = 'required'
            if form.is_valid():
                form.save()
                return redirect('login')
            return render(request, 'app_auth/passwd_reset_form.html', {'form': form})
        return HttpResponse('Token is not valid. Please request the new one.')


class ProfileEditView(LoginRequiredMixin, View):
    """
    Страница редактирования профиля пользователя
    """
    login_url = 'login'

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(request, 'app_auth/profile_edit.html', {'form': form, 'base_tpl': base_template(request.user)})

    def post(self, request):
        form = ProfileEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'app_auth/profile_edit.html', {'form': form, 'base_tpl': base_template(request.user)})


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Страница изменения пароля
    """
    template_name = 'app_auth/password_change.html'
    login_url = 'login'

    def get_form(self, form_class=None):
        form = super(ProfilePasswordChangeView, self).get_form(form_class)
        form.required_css_class = 'required'
        return form

    def get_success_url(self):
        return reverse('profile')

    def get_context_data(self, **kwargs):
        context = super(ProfilePasswordChangeView, self).get_context_data(**kwargs)
        context['base_tpl'] = base_template(self.request.user)
        return context


class ProfileConfirmView(View):
    """
    Страница завершения регистрации
    """
    def get(self, request, pk, token):
        account_activation_token = TokenGenerator()
        user = User.objects.get(id=pk)
        if account_activation_token.check_token(user, token):
            user.username = ''
            form = ProfileEditForm(instance=user)
            form.required_css_class = 'required'
            passwd = SetPasswordForm(user=user)
            passwd.required_css_class = 'required'
            return render(request, 'app_auth/user_confirm.html', {'form': form, 'passwd': passwd})
        return HttpResponse('Token is not valid. Please request the new one.')

    def post(self, request, pk, token):
        user = User.objects.get(id=pk)
        account_activation_token = TokenGenerator()
        if account_activation_token.check_token(user, token):
            form = ProfileEditForm(data=request.POST, instance=user)
            form.required_css_class = 'required'
            passwd = SetPasswordForm(data=request.POST, user=user)
            passwd.required_css_class = 'required'
            if form.is_valid() and passwd.is_valid():
                if form.cleaned_data['username'] != form.cleaned_data['email']:
                    user = form.save()
                    passwd.save()
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return redirect('profile')
                form.add_error('username', 'Имя пользователя не должно совпадать с электронной почтой!')
            return render(request, 'app_auth/user_confirm.html', {'form': form, 'passwd': passwd})
        return HttpResponse('Token is not valid. Please request the new one.')


class AdminCounterpartySelectView(View):
    """
    Страница выбора контрагента менеджера
    """

    def get(self, request):
        form = CounterpartySelectForm(queryset=Counterparty.objects.filter(admin=True))
        return render(
            request, 'app_auth/cp_select.html', {'form': form, 'owner_type': 'admin', 'owner_pk': None}
        )

    def post(self, request):
        form = CounterpartySelectForm(queryset=Counterparty.objects.filter(admin=True), data=request.POST)
        if form.is_valid():
            cp = form.cleaned_data['counterparty']
            return HttpResponse(json.dumps({'cp_id': str(cp.pk), 'cp_display': str(cp)}))
        return render(
            request, 'app_auth/cp_select.html', {'form': form, 'owner_type': 'admin', 'owner_pk': None}
        )


class ContractAddView(View):
    """
    Страница добавления договора
    """
    @staticmethod
    def get_object(request, obj_type, obj_pk):
        if obj_type == 'client':
            return Client.objects.get(pk=obj_pk)
        elif obj_type == 'contractor':
            return Contractor.objects.get(pk=obj_pk)
        raise ObjectDoesNotExist(f'No valid owner passed to view: {request.path}')

    def get(self, request, owner_type, owner_pk):
        form = get_contract_form(owner_type)()
        return render(request, 'app_auth/contract_add.html', {'form': form})

    def post(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = get_contract_form(owner_type)(request.POST)
        if form.is_valid():
            cp = form.save(commit=False)
            setattr(cp, owner_type, owner)
            cp.save()
            return redirect('select_contract', owner_type=owner_type, owner_pk=owner_pk)
        return render(request, 'app_auth/contract_add.html', {'form': form})


class ContractorContractEditView(UpdateView):
    """
    Страница редактирования договора с подрядчиком
    """
    template_name = 'app_auth/contract_edit.html'
    model = ContractorContract
    form_class = ContractorContractForm

    def get_success_url(self):
        return reverse('select_contract', kwargs={'owner_type': 'contractor', 'owner_pk': self.object.contractor.pk})


class ClientContractEditView(UpdateView):
    """
    Страница редактирования договора с клиентом
    """
    template_name = 'app_auth/contract_edit.html'
    model = ClientContract
    form_class = ClientContractForm

    def get_success_url(self):
        return reverse('select_contract', kwargs={'owner_type': 'client', 'owner_pk': self.object.client.pk})


class ContractSelectView(View):
    """
    Страница выбора договора
    """
    @staticmethod
    def get_object(request, obj_type, obj_pk):
        if obj_type == 'client':
            return Client.objects.get(pk=obj_pk)
        elif obj_type == 'contractor':
            return Contractor.objects.get(pk=obj_pk)
        raise ObjectDoesNotExist(f'No valid owner passed to view: {request.path}')

    def get(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = ContractSelectForm(queryset=owner.contracts.all())
        return render(
            request, 'app_auth/contract_select.html', {'form': form, 'owner_type': owner_type, 'owner_pk': owner_pk}
        )

    def post(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = ContractSelectForm(queryset=owner.contracts.all(), data=request.POST)
        if form.is_valid():
            contract = form.cleaned_data['contract']
            return HttpResponse(json.dumps({'contract_id': str(contract.pk), 'contract_display': str(contract)}))
        return render(
            request, 'app_auth/contract_select.html', {'form': form, 'owner_type': owner_type, 'owner_pk': owner_pk}
        )


class CounterpartySelectView(View):
    """
    Страница выбора контрагента
    """
    @staticmethod
    def get_object(request, obj_type, obj_pk):
        if obj_type == 'clients':
            return Client.objects.get(pk=obj_pk)
        elif obj_type == 'contractors':
            return Contractor.objects.get(pk=obj_pk)
        raise ObjectDoesNotExist(f'No valid owner passed to view: {request.path}')

    def get(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = CounterpartySelectForm(queryset=owner.counterparties.all())
        return render(
            request, 'app_auth/cp_select.html', {'form': form, 'owner_type': owner_type, 'owner_pk': owner_pk}
        )

    def post(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = CounterpartySelectForm(queryset=owner.counterparties.all(), data=request.POST)
        if form.is_valid():
            cp = form.cleaned_data['counterparty']
            return HttpResponse(json.dumps({'cp_id': str(cp.pk), 'cp_display': str(cp)}))
        return render(
            request, 'app_auth/cp_select.html', {'form': form, 'owner_type': owner_type, 'owner_pk': owner_pk}
        )


class AdminCounterpartyAddView(View):
    """
    Страница добавления контрагента менеджера
    """
    def get(self, request):
        form = CounterpartyForm()
        return render(request, 'app_auth/cp_add.html', {'form': form})

    def post(self, request):
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            cp = form.save(commit=False)
            cp.admin = True
            cp.save()
            return redirect('admin_select_cp')
        return render(request, 'app_auth/cp_add.html', {'form': form})


class CounterpartyAddView(View):
    """
    Страница добавления контрагента для клиента или подрядчика
    """
    @staticmethod
    def get_object(request, obj_type, obj_pk):
        if obj_type == 'clients':
            return Client.objects.get(pk=obj_pk)
        elif obj_type == 'contractors':
            return Contractor.objects.get(pk=obj_pk)
        raise ObjectDoesNotExist(f'No valid owner passed to view: {request.path}')

    def get(self, request, owner_type, owner_pk):
        form = CounterpartyForm()
        return render(request, 'app_auth/cp_add.html', {'form': form})

    def post(self, request, owner_type, owner_pk):
        owner = self.get_object(request, owner_type, owner_pk)
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            cp = form.save(commit=False)
            if owner_type == 'clients':
                cp.client = owner
            elif owner_type == 'contractors':
                cp.contractor = owner
            cp.save()
            return redirect('select_cp', owner_type=owner_type, owner_pk=owner_pk)
        return render(request, 'app_auth/cp_add.html', {'form': form})


class CounterpartyEditView(UpdateView):
    """
    Страница редактирования контрагента
    """
    model = Counterparty
    template_name = 'app_auth/cp_edit.html'
    form_class = CounterpartyForm

    def get_object(self, queryset=None):
        cp_id = self.request.resolver_match.kwargs['cp_id']
        return self.model.objects.get(pk=cp_id)

    def get_success_url(self):
        if self.object.client:
            owner_pk = self.object.client.pk
            owner_type = 'clients'
        elif self.object.contractor:
            owner_pk = self.object.contractor.pk
            owner_type = 'contractors'
        else:
            return reverse('admin_select_cp')
        return reverse('select_cp', kwargs={'owner_type': str(owner_type), 'owner_pk': str(owner_pk)})


class ContactsSelectView(View):
    """
    Страница выбора контактных лиц
    """

    def get(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactSelectForm(queryset=cp.contacts.all())
        return render(request, 'app_auth/contacts_select.html', {'form': form, 'cp_id': cp_id})

    def post(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactSelectForm(cp.contacts.all(), data=request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            return HttpResponse(json.dumps([{'contact_id': str(i.pk), 'contact_display': str(i)} for i in contact]))
        return render(request, 'app_auth/contacts_select.html', {'form': form, 'cp_id': cp_id})


class ConatactAddView(View):
    """
    Страница добавления контактного лица
    """

    def get(self, request, cp_id):
        form = ContactForm()
        return render(request, 'app_auth/contact_add.html', {'form': form})

    def post(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            similar_contacts = Contact.objects.filter(
                last_name=contact.last_name,
                first_name=contact.first_name,
            )
            if similar_contacts.exists():
                return redirect(
                    reverse('select_similar_contacts', kwargs={'cp_id': str(cp.pk)}) + '?' + urlencode({
                        'last_name': contact.last_name if contact.last_name else '',
                        'first_name': contact.first_name if contact.first_name else '',
                        'second_name': contact.second_name if contact.second_name else '',
                        'phone': contact.phone if contact.phone else '',
                        'email': contact.email if contact.email else '',
                    })
                )
            else:
                contact.save()
            contact.cp.add(cp)
            return redirect('select_contacts', cp_id=str(cp_id))
        return render(request, 'app_auth/contact_add.html', {'form': form})


class ContactTestMixin(UserPassesTestMixin):
    """
    Проверка доступа к редактированию контактного лица
    """
    @staticmethod
    def check_counterparty(org, cp_id):
        return org.counterparties.filter(pk=cp_id).exists()

    @staticmethod
    def get_org(user):
        if user.user_type == 'manager' or user.is_superuser:
            return '__all__'
        elif user.user_type.startswith('client'):
            return user.client
        elif user.user_type.startswith('contractor'):
            return user.contractor

    def test_func(self):
        org = self.get_org(self.request.user)
        cp_id = self.request.resolver_match.kwargs['cp_id']
        if org == '__all__':
            return True
        elif org is not None:
            return self.check_counterparty(org, cp_id)
        return False


class ContactEditView(ContactTestMixin, UpdateView):
    """
    Страница редактирования контактного лица
    """
    model = Contact
    template_name = 'app_auth/contact_edit.html'
    form_class = ContactForm

    def get_object(self, queryset=None):
        contact_id = self.request.resolver_match.kwargs['contact_id']
        return self.model.objects.get(pk=contact_id)

    def get_success_url(self):
        cp_id = self.request.resolver_match.kwargs['cp_id']
        return reverse('select_contacts', kwargs={'cp_id': cp_id})


class ContactDeleteView(ContactTestMixin, View):
    """
    Страница подтверждения удаления контактного лица
    """

    def get(self, request, cp_id, contact_id):
        contact = Contact.objects.get(pk=contact_id)
        return render(request, 'app_auth/contacts_delete.html', {'object': contact})

    def post(self, request, cp_id, contact_id):
        contact = Contact.objects.get(pk=contact_id)
        org = Counterparty.objects.get(pk=cp_id)
        org.contacts.remove(contact)
        if not any([contact.cp.exists(), contact.cnt_sent_transits.exists(), contact.cnt_received_transits.exists()]):
            contact.delete()
        return redirect('select_contacts', cp_id=cp_id)


class ContactSelectSimilarView(View):
    """
    Страница, предлагающая контактные лица, заведенные ранее в систему и похожие на введенное пользователем
    """

    def get(self, request, cp_id):
        data = request.GET
        contacts = Contact.objects.filter(last_name=data['last_name'], first_name=data['first_name'])
        save_anyway = urlencode({key: value for key, value in data.items() if value})
        return render(request, 'app_auth/contacts_select_similar.html', {'contacts': contacts, 'save_anyway': save_anyway})

    def post(self, request, cp_id):
        get_data = {key: value for key, value in request.GET.items()}
        post_data = request.POST
        cp = Counterparty.objects.get(pk=cp_id)
        if 'contact_id' in post_data:
            contact = Contact.objects.get(pk=post_data['contact_id'])
        elif get_data:
            contact = Contact(**get_data)
            contact.save()
        else:
            return HttpResponse('<>')
        contact.cp.add(cp)
        return HttpResponse('{"status": "ok"}')


def get_employees_list(request, client_pk):
    employees = [[str(i.pk), str(i)] for i in User.objects.filter(client_id=client_pk)]
    return HttpResponse(json.dumps(employees))
