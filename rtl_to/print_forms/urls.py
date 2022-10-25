from django.urls import path

from print_forms.views import waybill, WaybillPFDataAddView, \
    WaybillPFDataEditView, WaybillPFDataDeleteView, WaybillOriginalAddView, \
    DocOriginalEdit, DocOriginalDelete, segment_docs, OrigDocumentAddView

urlpatterns = [
    path('<uuid:segment_pk>/docs/', segment_docs, name='segment_docs'),
    path('<uuid:segment_pk>/waybill/add/', WaybillPFDataAddView.as_view(), name='waybill_data_add'),
    path('<uuid:segment_pk>/scan/add/', OrigDocumentAddView.as_view(), name='scan_add'),
    path('waybill/<uuid:waybill_pk>/<str:filename>', waybill, name='waybill'),
    path('waybill/<uuid:pk>/edit/', WaybillPFDataEditView.as_view(), name='waybill_edit'),
    path('waybill/<uuid:pk>/delete/', WaybillPFDataDeleteView.as_view(), name='waybill_delete'),
    path('waybill/<uuid:waybill_pk>/original/', WaybillOriginalAddView.as_view(), name='waybill_orig_add'),
    path('original/<uuid:pk>/edit/', DocOriginalEdit.as_view(), name='original_edit'),
    path('original/<uuid:pk>/delete/', DocOriginalDelete.as_view(), name='original_delete'),
]
