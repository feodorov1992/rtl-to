import os

from django.conf import settings
from django.shortcuts import render
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse

from orders.models import TransitSegment

DEFAULT_CSS = """
html {
    font-family: Montserrat, sans-serif;
    font-size: 10px;
    font-weight: normal;
    color: #000000;
    background-color: transparent;
    margin: 0;
    padding: 0;
    line-height: 150%;
    border: 1px none;
    display: inline;
    width: auto;
    height: auto;
    white-space: normal;
}

b,
strong {
    font-weight: bold;
}

i,
em {
    font-style: italic;
}

u {
    text-decoration: underline;
}

s,
strike {
    text-decoration: line-through;
}

a {
    text-decoration: underline;
    color: blue;
}

ins {
    color: green;
    text-decoration: underline;
}
del {
    color: red;
    text-decoration: line-through;
}

pre,
code,
kbd,
samp,
tt {
    font-family: "Courier New";
}

h1,
h2,
h3,
h4,
h5,
h6 {
    font-weight:bold;
    -pdf-outline: true;
    -pdf-outline-open: false;
}

h1 {
    /*18px via YUI Fonts CSS foundation*/
    font-size:138.5%;
    -pdf-outline-level: 0;
}

h2 {
    /*16px via YUI Fonts CSS foundation*/
    font-size:123.1%;
    -pdf-outline-level: 1;
}

h3 {
    /*14px via YUI Fonts CSS foundation*/
    font-size:108%;
    -pdf-outline-level: 2;
}

h4 {
    -pdf-outline-level: 3;
}

h5 {
    -pdf-outline-level: 4;
}

h6 {
    -pdf-outline-level: 5;
}

h1,
h2,
h3,
h4,
h5,
h6,
p,
pre,
hr {
    margin:1em 0;
}

address,
blockquote,
body,
center,
dl,
dir,
div,
fieldset,
form,
h1,
h2,
h3,
h4,
h5,
h6,
hr,
isindex,
menu,
noframes,
noscript,
ol,
p,
pre,
table,
th,
tr,
td,
ul,
li,
dd,
dt,
pdftoc {
    display: block;
}

table {
}

tr,
th,
td {

    vertical-align: middle;
    width: auto;
}

th {
    text-align: center;
    font-weight: bold;
}

center {
    text-align: center;
}

big {
    font-size: 125%;
}

small {
    font-size: 75%;
}


ul {
    margin-left: 1.5em;
    list-style-type: disc;
}

ul ul {
    list-style-type: circle;
}

ul ul ul {
    list-style-type: square;
}

ol {
    list-style-type: decimal;
    margin-left: 1.5em;
}

pre {
    white-space: pre;
}

blockquote {
    margin-left: 1.5em;
    margin-right: 1.5em;
}

noscript {
    display: none;
}
"""

def fetch_pdf_resources(uri, rel):
    if uri.find(settings.STATIC_URL) != -1:
        return os.path.join(settings.BASE_DIR, 'static', *os.path.split(uri.replace(settings.STATIC_URL, '')))
    return None


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    # pdf = pisa.pisaDocument(html, result, encoding='utf-8', link_callback=fetch_pdf_resources, default_css=DEFAULT_CSS)
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=fetch_pdf_resources)
    print(pdf.getFontName('Montserrat'))
    print(pdf.fontList)
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
    return render(request, 'print_forms/base_album.html', context)
