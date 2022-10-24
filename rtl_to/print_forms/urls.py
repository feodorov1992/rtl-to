from django.urls import path

from print_forms.views import waybill, waybill_page, waybill_no_name

urlpatterns = [
    path('<uuid:segment_pk>/waybill/', waybill_no_name, name='waybill_no_name'),
    path('<uuid:segment_pk>/waybill/<str:filename>', waybill, name='waybill'),
    path('<uuid:segment_pk>/waybill_page/', waybill_page, name='waybill_page')
]
