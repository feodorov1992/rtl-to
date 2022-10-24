import os

import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string

from rtl_to import settings


class PDFGenerator:
    OPENED_FILES = list()

    def __init__(self, output_name):
        self.filename = output_name if output_name.endswith('pdf') else f'{output_name}.pdf'
        self.temp_file_path = os.path.join(settings.MEDIA_ROOT, self.filename)
        self.temp_file_path = os.path.normpath(self.temp_file_path)
        self.context = {'filename': self.filename}

    def response(self, template_name, context):
        self.context.update(context)
        pdf = self.file(self.temp_file_path, template_name, self.context)
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        # response['Content-Disposition'] = 'inline; filename="{}"'.format(self.filename)
        return response

    def file(self, file_path, template_name, context):
        html = render_to_string(template_name, context)
        options = {
            "enable-local-file-access": None
        }
        pdfkit.from_string(html, file_path, options=options)
        file = open(file_path, 'rb')
        self.OPENED_FILES.append(file)
        return file

    def __del__(self):
        for file in self.OPENED_FILES:
            file.close()
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
