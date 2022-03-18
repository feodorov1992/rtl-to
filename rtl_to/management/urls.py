from django.urls import path

from management.views import dashboard, OrgListView, UserListView, OrgAddView, OrgDetailView, OrgEditView, \
    OrgDeleteView, UserAddView, UserEditView, UserDeleteView, UserDetailView

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('organisations/', OrgListView.as_view(), name='orgs_list'),
    path('organisations/add/', OrgAddView.as_view(), name='orgs_add'),
    path('organisations/<uuid:pk>', OrgDetailView.as_view(), name='orgs_detail'),
    path('organisations/<uuid:pk>/edit/', OrgEditView.as_view(), name='orgs_edit'),
    path('organisations/<uuid:pk>/delete/', OrgDeleteView.as_view(), name='orgs_delete'),
    path('users/', UserListView.as_view(), name='users_list'),
    path('users/add/', UserAddView.as_view(), name='user_add'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
