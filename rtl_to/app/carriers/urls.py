from django.urls import path

from carriers.views import dashboard, UserListView, UserAddView, UserEditView, UserDeleteView, UserDetailView, \
    OrderDetailView, OrderListView, OrderEditView, SegmentsEditView, CarrierGetOrderView, CarrierReportsView, \
    CarrierReportsCreateView, CarrierReportUpdateView, CarrierReportDeleteView

urlpatterns = [
    path('', dashboard, name='dashboard_carrier'),
    path('users/', UserListView.as_view(), name='users_list_carrier'),
    path('users/add/', UserAddView.as_view(), name='user_add_carrier'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail_carrier'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit_carrier'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete_carrier'),
    path('orders/', OrderListView.as_view(), name='orders_list_carrier'),
    path('orders/<uuid:pk>', OrderDetailView.as_view(), name='order_detail_carrier'),
    path('orders/<uuid:pk>/edit/', OrderEditView.as_view(), name='order_edit_carrier'),
    path('orders/<uuid:pk>/segments/', SegmentsEditView.as_view(), name='order_segments_carrier'),
    path('orders/<uuid:pk>/manager_get/', CarrierGetOrderView.as_view(), name='carrier_get'),
    path('reports/', CarrierReportsView.as_view(), name='reports_carrier'),
    path('reports/create/', CarrierReportsCreateView.as_view(), name='reports_create_carrier'),
    path('reports/<uuid:report_id>/update/', CarrierReportUpdateView.as_view(), name='reports_update_carrier'),
    path('reports/<uuid:report_id>/delete/', CarrierReportDeleteView.as_view(), name='reports_delete_carrier'),
]
