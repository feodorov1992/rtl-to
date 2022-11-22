from django.urls import path

from print_forms.views import waybill, WaybillPFDataAddView, \
    WaybillPFDataEditView, WaybillPFDataDeleteView, WaybillOriginalAddView, \
    DocOriginalEdit, DocOriginalDelete, segment_docs, OrigDocumentAddView, shipping_receipt, shipping_receipt_ext, \
    ext_order_blank

urlpatterns = [
    path('<uuid:segment_pk>/docs/', segment_docs, name='segment_docs'),
    path('<uuid:segment_pk>/waybill/add/', WaybillPFDataAddView.as_view(), name='waybill_data_add'),
    path('<uuid:segment_pk>/scan/add/', OrigDocumentAddView.as_view(), name='scan_add'),
    path('docs/<uuid:docdata_pk>/waybill/<str:filename>', waybill, name='waybill'),
    path('docs/<uuid:docdata_pk>/shipping_receipt/<str:filename>', shipping_receipt, name='shipping_receipt'),
    path('docs/<uuid:transit_pk>/shipping_receipt_ext/<str:filename>', shipping_receipt_ext, name='shipping_receipt_ext'),
    path('docs/<uuid:order_pk>/ext_order_blank/<str:filename>', ext_order_blank, name='ext_order_blank'),
    path('waybill/<uuid:pk>/edit/', WaybillPFDataEditView.as_view(), name='waybill_edit'),
    path('waybill/<uuid:pk>/delete/', WaybillPFDataDeleteView.as_view(), name='waybill_delete'),
    path('waybill/<uuid:waybill_pk>/original/', WaybillOriginalAddView.as_view(), name='waybill_orig_add'),
    path('original/<uuid:pk>/edit/', DocOriginalEdit.as_view(), name='original_edit'),
    path('original/<uuid:pk>/delete/', DocOriginalDelete.as_view(), name='original_delete'),
]
