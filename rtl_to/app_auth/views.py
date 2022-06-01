from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from app_auth.forms import ProfileEditForm
from app_auth.mailer import send_technical_mail
from app_auth.tokens import TokenGenerator
from app_auth.models import User
from django.views import View


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'app_auth/profile.html', {})


def forgot_password_confirm(request):
    return render(request, 'app_auth/forgot_password_confirm.html', {})


class UserLoginView(LoginView):
    template_name = 'app_auth/login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('dashboard')
        else:
            return reverse('dashboard_pub')


class UserLogoutView(LogoutView):

    def get_success_url(self):
        return reverse('home')


class ForgotPasswordView(View):

    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'app_auth/passwd_restore.html', {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
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
            return render(request, 'app_auth/passwd_reset_form.html', {'form': form})
        return HttpResponse('Token is not valid. Please request the new one.')

    def post(self, request, pk, token):
        account_activation_token = TokenGenerator()
        user = User.objects.get(id=pk)
        if account_activation_token.check_token(user, token):
            form = SetPasswordForm(data=request.POST, user=user)
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

    def get_success_url(self):
        return reverse('profile')


class ProfileConfirmView(View):

    def get(self, request, pk, token):
        account_activation_token = TokenGenerator()
        user = User.objects.get(id=pk)
        if account_activation_token.check_token(user, token):
            user.username = ''
            form = ProfileEditForm(instance=user)
            passwd = SetPasswordForm(user=user)
            return render(request, 'app_auth/user_confirm.html', {'form': form, 'passwd': passwd})
        return HttpResponse('Token is not valid. Please request the new one.')

    def post(self, request, pk, token):
        user = User.objects.get(id=pk)
        account_activation_token = TokenGenerator()
        if account_activation_token.check_token(user, token):
            form = ProfileEditForm(data=request.POST, instance=user)
            passwd = SetPasswordForm(data=request.POST, user=user)
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
