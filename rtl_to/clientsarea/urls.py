from django.urls import path

from clientsarea.views import dashboard, UserListView, UserAddView, UserEditView, UserDeleteView, UserDetailView, \
    OrderCreateView, OrderDetailView, OrderFileUpload, CustomerGetOrderView, OrderListView, CancelOrderView, \
    OrderHistoryView

urlpatterns = [
    path('', dashboard, name='dashboard_pub'),
    path('users/', UserListView.as_view(), name='users_list_pub'),
    path('users/add/', UserAddView.as_view(), name='user_add_pub'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail_pub'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit_pub'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete_pub'),
    path('orders/', OrderListView.as_view(), name='orders_list_pub'),
    path('orders/add/', OrderCreateView.as_view(), name='order_add_pub'),
    path('orders/<uuid:pk>', OrderDetailView.as_view(), name='order_detail_pub'),
    path('orders/<uuid:pk>/docs_edit/', OrderFileUpload.as_view(), name='docs_edit_pub'),
    path('orders/<uuid:pk>/manager_get/', CustomerGetOrderView.as_view(), name='customer_get'),
    path('orders/<uuid:pk>/cancel/', CancelOrderView.as_view(), name='order_cancel_pub'),
    path('orders/<uuid:pk>/history/', OrderHistoryView.as_view(), name='order_history_pub')
]
