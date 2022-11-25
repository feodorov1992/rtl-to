from django.urls import path

from print_forms.views import waybill, WaybillPFDataAddView, WaybillPFDataEditView, WaybillPFDataDeleteView, \
    DocOriginalEdit, DocOriginalDelete, segment_docs, OrigDocumentAddView, shipping_receipt, shipping_receipt_ext, \
    ext_order_blank, TransDocAddView, TransDocPFDataEditView, ReceiptOriginalAddView, ReceiptOriginalEditView, \
    ReceiptOriginalDeleteView

urlpatterns = [
    path('<uuid:segment_pk>/docs/', segment_docs, name='segment_docs'),
    path('<uuid:segment_pk>/waybill/add/', WaybillPFDataAddView.as_view(), name='waybill_data_add'),
    path('<uuid:segment_pk>/trans_doc/add/', TransDocAddView.as_view(), name='trans_doc_data_add'),
    path('<uuid:segment_pk>/original/add/', OrigDocumentAddView.as_view(), name='original_add'),
    path('<uuid:segment_pk>/receipt_original/add/', ReceiptOriginalAddView.as_view(), name='receipt_original_add'),
    path('docs/<uuid:docdata_pk>/waybill/<str:filename>', waybill, name='waybill'),
    path('docs/<uuid:docdata_pk>/shipping_receipt/<str:filename>', shipping_receipt, name='shipping_receipt'),
    path('docs/<uuid:transit_pk>/shipping_receipt_ext/<str:filename>', shipping_receipt_ext, name='shipping_receipt_ext'),
    path('docs/<uuid:order_pk>/ext_order_blank/<str:filename>', ext_order_blank, name='ext_order_blank'),
    path('waybill/<uuid:pk>/edit/', WaybillPFDataEditView.as_view(), name='waybill_edit'),
    path('trans_doc/<uuid:pk>/edit/', TransDocPFDataEditView.as_view(), name='trans_doc_edit'),
    path('waybill/<uuid:pk>/delete/', WaybillPFDataDeleteView.as_view(), name='waybill_delete'),
    path('original/<uuid:pk>/edit/', DocOriginalEdit.as_view(), name='original_edit'),
    path('original/<uuid:pk>/delete/', DocOriginalDelete.as_view(), name='original_delete'),
    path('receipt_original/<uuid:pk>/edit/', ReceiptOriginalEditView.as_view(), name='receipt_original_edit'),
    path('receipt_original/<uuid:pk>/delete/', ReceiptOriginalDeleteView.as_view(), name='receipt_original_delete'),
]
