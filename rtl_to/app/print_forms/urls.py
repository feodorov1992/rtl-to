from django.urls import path

from print_forms.views import waybill, WaybillPFDataAddView, WaybillPFDataEditView, WaybillPFDataDeleteView, \
    DocOriginalEdit, DocOriginalDelete, segment_docs, OrigDocumentAddView, shipping_receipt, shipping_receipt_ext, \
    ext_order_blank, TransDocAddView, TransDocPFDataEditView, ReceiptOriginalAddView, ReceiptOriginalEditView, \
    ReceiptOriginalDeleteView, bills_blank, contractor_act_blank, contractor_bill_blank, order_blank, \
    RandomDocScanAddView, RandomDocScanEdit, RandomDocScanDelete, InternalBillsBlank, InternationalBillsBlank

urlpatterns = [
    path('<uuid:segment_pk>/docs/', segment_docs, name='segment_docs'),
    path('<uuid:segment_pk>/waybill/add/', WaybillPFDataAddView.as_view(), name='waybill_data_add'),
    path('<uuid:segment_pk>/trans_doc/add/', TransDocAddView.as_view(), name='trans_doc_data_add'),
    path('<uuid:segment_pk>/original/add/', OrigDocumentAddView.as_view(), name='original_add'),
    path('<uuid:segment_pk>/random/add/', RandomDocScanAddView.as_view(), name='random_doc_add'),
    path('<uuid:segment_pk>/receipt_original/add/', ReceiptOriginalAddView.as_view(), name='receipt_original_add'),
    path('docs/<uuid:docdata_pk>/waybill/<str:filename>', waybill, name='waybill'),
    path('docs/<uuid:docdata_pk>/shipping_receipt/<str:filename>', shipping_receipt, name='shipping_receipt'),
    path('docs/<uuid:transit_pk>/shipping_receipt_ext/<str:filename>', shipping_receipt_ext, name='shipping_receipt_ext'),
    path('docs/<uuid:order_pk>/order_blank/<str:filename>', order_blank, name='order_blank'),
    path('docs/<uuid:order_pk>/ext_order_blank/<str:filename>', ext_order_blank, name='ext_order_blank'),
    path('docs/<uuid:order_pk>/contractor_act_blank/<str:filename>', contractor_act_blank, name='contractor_act_blank'),
    path('docs/<uuid:order_pk>/contractor_bill_blank/<str:filename>', contractor_bill_blank, name='contractor_bill_blank'),
    path('waybill/<uuid:pk>/edit/', WaybillPFDataEditView.as_view(), name='waybill_edit'),
    path('trans_doc/<uuid:pk>/edit/', TransDocPFDataEditView.as_view(), name='trans_doc_edit'),
    path('waybill/<uuid:pk>/delete/', WaybillPFDataDeleteView.as_view(), name='waybill_delete'),
    path('original/<uuid:pk>/edit/', DocOriginalEdit.as_view(), name='original_edit'),
    path('original/<uuid:pk>/delete/', DocOriginalDelete.as_view(), name='original_delete'),
    path('random/<uuid:pk>/edit/', RandomDocScanEdit.as_view(), name='random_doc_edit'),
    path('random/<uuid:pk>/delete/', RandomDocScanDelete.as_view(), name='random_doc_delete'),
    path('receipt_original/<uuid:pk>/edit/', ReceiptOriginalEditView.as_view(), name='receipt_original_edit'),
    path('receipt_original/<uuid:pk>/delete/', ReceiptOriginalDeleteView.as_view(), name='receipt_original_delete'),
    path('bills_blank/<str:filename>', bills_blank, name='bills_blank'),
    path('bills_blank_internal/<str:filename>', InternalBillsBlank.as_view(), name='bills_blank_internal'),
    path('bills_blank_international/<str:filename>', InternationalBillsBlank.as_view(), name='bills_blank_international')
]
