from django.urls import path

from print_forms.views import waybill

urlpatterns = [
    path('<uuid:segment_pk>/waybill/', waybill, name='waybill'),
]
