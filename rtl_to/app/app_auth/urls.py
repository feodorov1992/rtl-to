from django.urls import path

from app_auth.views import profile_view, ProfileEditView, ProfilePasswordChangeView, UserLoginView, UserLogoutView, \
    ForgotPasswordView, forgot_password_confirm, PasswordRestoreView, ProfileConfirmView, CounterpartySelectView, \
    CounterpartyAddView, ContactsSelectView, ConatactAddView, ContactSelectSimilarView, ContactDeleteView, \
    ContactEditView, CounterpartyEditView, AdminCounterpartySelectView, AdminCounterpartyAddView, ContractSelectView, \
    ContractAddView, ContractorContractEditView, ClientContractEditView, get_employees_list

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
    path('<str:owner_type>/<uuid:owner_pk>/cp_select', CounterpartySelectView.as_view(), name='select_cp'),
    path('<str:owner_type>/<uuid:owner_pk>/contract_select', ContractSelectView.as_view(), name='select_contract'),
    path('admin/cp_select', AdminCounterpartySelectView.as_view(), name='admin_select_cp'),
    path('<str:owner_type>/<uuid:owner_pk>/cp_add', CounterpartyAddView.as_view(), name='add_cp'),
    path('<str:owner_type>/<uuid:owner_pk>/contract_add', ContractAddView.as_view(), name='add_contract'), ###
    path('contractor/contracts/<uuid:pk>/edit', ContractorContractEditView.as_view(), name='edit_contractor_contract'),
    path('client/contracts/<uuid:pk>/edit', ClientContractEditView.as_view(), name='edit_client_contract'),
    path('client/<uuid:client_pk>/employees', get_employees_list, name='get_client_employees_list'),
    path('<str:owner_type>/contracts/<uuid:contract_pk>/delete', CounterpartyAddView.as_view(), name='delete_contract'), ###
    path('admin/cp_add', AdminCounterpartyAddView.as_view(), name='admin_add_cp'),
    path('counterparties/<uuid:cp_id>/edit', CounterpartyEditView.as_view(), name='edit_cp'),
    path('counterparties/<uuid:cp_id>/contacts_select', ContactsSelectView.as_view(), name='select_contacts'),
    path('counterparties/<uuid:cp_id>/contacts_add', ConatactAddView.as_view(), name='add_contacts'),
    path('counterparties/<uuid:cp_id>/contacts/<uuid:contact_id>/edit', ContactEditView.as_view(), name='edit_contacts'),
    path('counterparties/<uuid:cp_id>/contacts/<uuid:contact_id>/delete', ContactDeleteView.as_view(), name='delete_contacts'),
    path('counterparties/<uuid:cp_id>/contacts_select_similar', ContactSelectSimilarView.as_view(), name='select_similar_contacts')
]
