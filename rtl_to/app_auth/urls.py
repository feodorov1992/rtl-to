from django.urls import path

from app_auth.views import profile_view, ProfileEditView, ProfilePasswordChangeView, UserLoginView, UserLogoutView, \
    ForgotPasswordView, forgot_password_confirm, PasswordRestoreView, ProfileConfirmView

urlpatterns = [
    path('', profile_view, name='profile'),
    path('edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('change_password/', ProfilePasswordChangeView.as_view(), name='change_password'),
    path('login/', UserLoginView.as_view(next_page='profile'), name='login'),
    path('logout/', UserLogoutView.as_view(next_page='/'), name='logout'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot_password/confirm/', forgot_password_confirm, name='forgot_password_confirm'),
    path('restore_password/<uuid:pk>/<str:token>/', PasswordRestoreView.as_view(), name='restore_password'),
    path('registration_confirm/<uuid:pk>/<str:token>/', ProfileConfirmView.as_view(), name='registration_confirm'),
]
