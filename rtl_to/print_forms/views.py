import os

import pdfkit
from django.conf import settings
from django.shortcuts import render
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse

from orders.models import TransitSegment


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.STATIC_URL) != -1:
        return os.path.join(settings.BASE_DIR, 'static', *os.path.split(uri.replace(settings.STATIC_URL, '')))
    return None


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pdfkit.from_string(html, result)
    # pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=fetch_pdf_resources)
    # print(pdf.getFontName('Montserrat'))
    # print(pdf.fontList)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % pdf.err)


def waybill(request, segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)
    context = {'pagesize': 'A4', 'segment': segment}
    return render_to_pdf('print_forms/base_album.html', context)


def waybill_page(request, segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)
    context = {'pagesize': 'A4', 'segment': segment}
    print(type(render(request, 'print_forms/base_album.html', context)))
    return render(request, 'print_forms/base_album.html', context)
