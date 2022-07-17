import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import classonlymethod
from django.utils.http import urlencode

from app_auth.forms import ProfileEditForm, CounterpartySelectForm, CounterpartyCreateForm, ContactSelectForm, \
    ContactCreateForm
from app_auth.mailer import send_technical_mail
from app_auth.tokens import TokenGenerator
from app_auth.models import User, Client, Counterparty, Contact
from django.views import View


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'app_auth/profile.html', {})


def forgot_password_confirm(request):
    return render(request, 'app_auth/forgot_password_confirm.html', {})


class UserLoginView(LoginView):
    template_name = 'app_auth/login.html'

    def get_form(self, form_class=None):
        form = super(UserLoginView, self).get_form(form_class)
        form.required_css_class = 'required'
        return form

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('dashboard')
        else:
            return reverse('dashboard_pub')


class UserLogoutView(LogoutView):

    @staticmethod
    def get_success_url():
        return reverse('home')


class ForgotPasswordView(View):

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
    login_url = 'login'

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(request, 'app_auth/profile_edit.html', {'form': form})

    def post(self, request):
        form = ProfileEditForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'app_auth/profile_edit.html', {'form': form})


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'app_auth/password_change.html'
    login_url = 'login'

    def get_form(self, form_class=None):
        form = super(ProfilePasswordChangeView, self).get_form(form_class)
        form.required_css_class = 'required'
        return form

    def get_success_url(self):
        return reverse('profile')


class ProfileConfirmView(View):

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


class CounterpartySelectView(View):

    def get(self, request, client_pk):
        client = Client.objects.get(pk=client_pk)
        form = CounterpartySelectForm(queryset=client.counterparties.all())
        return render(request, 'app_auth/cp_select.html', {'form': form})

    def post(self, request, client_pk):
        client = Client.objects.get(pk=client_pk)
        form = CounterpartySelectForm(queryset=client.counterparties.all(), data=request.POST)
        if form.is_valid():
            cp = form.cleaned_data['counterparty']
            return HttpResponse(json.dumps({'cp_id': str(cp.pk), 'cp_display': str(cp)}))
        return render(request, 'app_auth/cp_select.html', {'form': form})


class CounterpartyAddView(View):

    def get(self, request, client_pk):
        form = CounterpartyCreateForm()
        return render(request, 'app_auth/cp_add.html', {'form': form})

    def post(self, request, client_pk):
        client = Client.objects.get(pk=client_pk)
        form = CounterpartyCreateForm(request.POST)
        if form.is_valid():
            cp = form.save(commit=False)
            cp.client = client
            cp.save()
            return redirect('select_cp', client_pk=client_pk)
        return render(request, 'app_auth/cp_add.html', {'form': form})


class ContactsSelectView(View):

    def get(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactSelectForm(queryset=cp.contacts.all())
        return render(request, 'app_auth/contacts_select.html', {'form': form})

    def post(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactSelectForm(cp.contacts.all(), data=request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            return HttpResponse(json.dumps([{'contact_id': str(i.pk), 'contact_display': str(i)} for i in contact]))
        return render(request, 'app_auth/contacts_select.html', {'form': form})


class ConatactAddView(View):

    def get(self, request, cp_id):
        form = ContactCreateForm()
        return render(request, 'app_auth/contact_add.html', {'form': form})

    def post(self, request, cp_id):
        cp = Counterparty.objects.get(pk=cp_id)
        form = ContactCreateForm(request.POST)
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


class ContactSelectSimilarView(View):

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
