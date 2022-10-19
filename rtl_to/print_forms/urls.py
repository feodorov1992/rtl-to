from django.urls import path

from print_forms.views import waybill, waybill_page

urlpatterns = [
    path('<uuid:segment_pk>/waybill/', waybill, name='waybill'),
    path('<uuid:segment_pk>/waybill_page/', waybill_page, name='waybill_page')
]
