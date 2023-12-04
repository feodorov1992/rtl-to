from django.conf import settings


def branding(request):

    return {
        'branding_files': settings.BRANDING.static_files(),
        'requisites': settings.BRANDING.requisites
    }
