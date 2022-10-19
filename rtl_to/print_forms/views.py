from django.shortcuts import render
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse

from orders.models import TransitSegment


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(html, result, encoding='utf-8', path='127.0.0.1')

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % pdf.err)


def waybill(request, segment_pk):
    segment = TransitSegment.objects.get(pk=segment_pk)
    context = {'pagesize': 'A4', 'segment': segment}
    print(request.environ['REMOTE_ADDR'])
    return render_to_pdf('print_forms/base_album.html', context)
