from django.urls import path, include

from management.views import dashboard, ClientsListView, UserListView, ClientAddView, ClientDetailView, \
    ClientEditView, ClientDeleteView, UserAddView, UserEditView, UserDeleteView, UserDetailView, OrderListView, \
    OrderEditView, OrderDetailView, OrderCreateView, OrderDeleteView, OrderHistoryEditView, TransitHistoryEditView, \
    ManagerGetOrderView, ContractorListView, ContractorAddView, ContractorDetailView, ContractorEditView, \
    ContractorDeleteView, OrderFileUpload, OrderHistoryView, AuditorsListView, AuditorAddView, \
    AuditorDetailView, AuditorEditView, AuditorDeleteView, AgentAddView, ReportsView, ReportsCreateView, \
    ReportUpdateView, ReportDeleteView, ExtOrderEditView, cargos_spreadsheet, resend_registration_mail, BillOutputView, \
    BillOutputPostView

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('clients/', ClientsListView.as_view(), name='clients_list'),
    path('clients/add/', ClientAddView.as_view(), name='client_add'),
    path('clients/<uuid:pk>', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<uuid:pk>/edit/', ClientEditView.as_view(), name='client_edit'),
    path('clients/<uuid:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('auditors/', AuditorsListView.as_view(), name='auditors_list'),
    path('auditors/add/', AuditorAddView.as_view(), name='auditor_add'),
    path('auditors/<uuid:pk>', AuditorDetailView.as_view(), name='auditor_detail'),
    path('auditors/<uuid:pk>/edit/', AuditorEditView.as_view(), name='auditor_edit'),
    path('auditors/<uuid:pk>/delete/', AuditorDeleteView.as_view(), name='auditor_delete'),
    path('auditors/add_agent/', AgentAddView.as_view(), name='agent_add'),
    path('contractors/', ContractorListView.as_view(), name='contractors_list'),
    path('contractors/add/', ContractorAddView.as_view(), name='contractor_add'),
    path('contractors/<uuid:pk>', ContractorDetailView.as_view(), name='contractor_detail'),
    path('contractors/<uuid:pk>/edit/', ContractorEditView.as_view(), name='contractor_edit'),
    path('contractors/<uuid:pk>/delete/', ContractorDeleteView.as_view(), name='contractor_delete'),
    path('users/', UserListView.as_view(), name='users_list'),
    path('users/add/', UserAddView.as_view(), name='user_add'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<uuid:pk>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<uuid:pk>/resend_registration_mail/', resend_registration_mail, name='resend_registration_mail'),
    path('orders/', OrderListView.as_view(), name='orders_list'),
    # path('orders/calc/', OrderCalcView.as_view(), name='order_calc'),
    path('orders/add/', OrderCreateView.as_view(), name='order_add'),
    path('orders/<uuid:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<uuid:pk>/edit/', OrderEditView.as_view(), name='order_edit'),
    path('orders/<uuid:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/<uuid:pk>/status_edit/', OrderHistoryEditView.as_view(), name='order_status_edit'),
    path('transits/<uuid:pk>/status_edit/', TransitHistoryEditView.as_view(), name='transit_status_edit'),
    # path('transits/<uuid:pk>/segments_edit/', SegmentsEditView.as_view(), name='segments_edit'),
    path('transits/<uuid:pk>/ext_orders_edit/', ExtOrderEditView.as_view(), name='ext_orders_edit'),
    path('orders/<uuid:pk>/manager_get/', ManagerGetOrderView.as_view(), name='manager_get'),
    path('orders/<uuid:pk>/docs_edit/', OrderFileUpload.as_view(), name='docs_edit'),
    path('orders/<uuid:pk>/history/', OrderHistoryView.as_view(), name='order_history'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('reports/create/', ReportsCreateView.as_view(), name='reports_create'),
    path('reports/<uuid:report_id>/update/', ReportUpdateView.as_view(), name='reports_update'),
    path('reports/<uuid:report_id>/delete/', ReportDeleteView.as_view(), name='reports_delete'),
    path('orders/cargos_spreadsheet', cargos_spreadsheet, name='cargos_spreadsheet'),
    path('bill_output/', BillOutputView.as_view(), name='bill_output'),
    path('bill_output/post/', BillOutputPostView.as_view(), name='post_for_bills')
]
