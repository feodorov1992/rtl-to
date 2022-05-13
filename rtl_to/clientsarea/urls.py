from django.urls import path

from clientsarea.views import dashboard, UserListView, UserAddView, UserEditView, UserDeleteView, UserDetailView

urlpatterns = [
    path('', dashboard, name='dashboard_pub'),
    path('users/', UserListView.as_view(), name='users_list_pub'),
    path('users/add/', UserAddView.as_view(), name='user_add_pub'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail_pub'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit_pub'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete_pub'),
]
