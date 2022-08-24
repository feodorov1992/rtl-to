from django.urls import path

from app_auth.views import profile_view, ProfileEditView, ProfilePasswordChangeView, UserLoginView, UserLogoutView, \
    ForgotPasswordView, forgot_password_confirm, PasswordRestoreView, ProfileConfirmView, CounterpartySelectView, \
    CounterpartyAddView, ContactsSelectView, ConatactAddView, ContactSelectSimilarView, ContactDeleteView, \
    ContactEditView, CounterpartyEditView

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
    path('clients/<uuid:client_pk>/cp_select', CounterpartySelectView.as_view(), name='select_cp'),
    path('clients/<uuid:client_pk>/cp_add', CounterpartyAddView.as_view(), name='add_cp'),
    path('counterparties/<uuid:cp_id>/edit', CounterpartyEditView.as_view(), name='edit_cp'),
    path('counterparties/<uuid:cp_id>/contacts_select', ContactsSelectView.as_view(), name='select_contacts'),
    path('counterparties/<uuid:cp_id>/contacts_add', ConatactAddView.as_view(), name='add_contacts'),
    path('counterparties/<uuid:cp_id>/contacts/<uuid:contact_id>/edit', ContactEditView.as_view(), name='edit_contacts'),
    path('counterparties/<uuid:cp_id>/contacts/<uuid:contact_id>/delete', ContactDeleteView.as_view(), name='delete_contacts'),
    path('counterparties/<uuid:cp_id>/contacts_select_similar', ContactSelectSimilarView.as_view(), name='select_similar_contacts')
]
