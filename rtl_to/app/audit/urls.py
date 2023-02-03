from django.urls import path

from audit.views import dashboard, UserListView, UserAddView, UserEditView, UserDeleteView, UserDetailView, \
    OrderDetailView, OrderListView, OrderHistoryView

urlpatterns = [
    path('', dashboard, name='dashboard_aud'),
    path('users/', UserListView.as_view(), name='users_list_aud'),
    path('users/add/', UserAddView.as_view(), name='user_add_aud'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail_aud'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit_aud'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete_aud'),
    path('orders/', OrderListView.as_view(), name='orders_list_aud'),
    path('orders/<uuid:pk>', OrderDetailView.as_view(), name='order_detail_aud'),
    path('orders/<uuid:pk>/history/', OrderHistoryView.as_view(), name='order_history_aud')
]
