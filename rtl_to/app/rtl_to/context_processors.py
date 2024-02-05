from django.conf import settings

from app_auth.models import OrderLabelManager


def branding(request):

    return {
        'branding_files': settings.BRANDING.static_files(),
        'requisites': settings.BRANDING.requisites,
        'coloring': settings.BRANDING.coloring
    }


def order_label_management(request):
    if hasattr(request.user, 'client') and request.user.client:
        return {'corp_order_label': OrderLabelManager(request.user.client.order_label)}
    return {'corp_order_label': OrderLabelManager()}
