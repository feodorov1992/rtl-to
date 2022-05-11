from django.urls import path

from management.views import dashboard, ClientsListView, UserListView, ClientAddView, ClientDetailView, ClientEditView, \
    ClientDeleteView, UserAddView, UserEditView, UserDeleteView, UserDetailView, OrderListView, OrderEditView, \
    OrderDetailView, OrderCreateView, OrderDeleteView, OrderCalcView

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('clients/', ClientsListView.as_view(), name='clients_list'),
    path('clients/add/', ClientAddView.as_view(), name='client_add'),
    path('clients/<uuid:pk>', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<uuid:pk>/edit/', ClientEditView.as_view(), name='client_edit'),
    path('clients/<uuid:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('users/', UserListView.as_view(), name='users_list'),
    path('users/add/', UserAddView.as_view(), name='user_add'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/calc/', OrderCalcView.as_view(), name='order_calc'),
    path('orders/add/', OrderCreateView.as_view(), name='order_add'),
    path('orders/<uuid:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<uuid:pk>/edit/', OrderEditView.as_view(), name='order_edit'),
    path('orders/<uuid:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
]
