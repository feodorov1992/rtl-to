import os
import uuid

import PyPDF2

import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string

from rtl_to import settings


class PDFGenerator:
    OPENED_FILES = list()
    OPENED_FILES_PATHS = list()

    def __init__(self, output_name):
        self.filename = output_name if output_name.endswith('pdf') else f'{output_name}.pdf'
        self.temp_file_path = os.path.join(settings.MEDIA_ROOT, self.filename)
        self.temp_file_path = os.path.normpath(self.temp_file_path)
        self.context = {'filename': self.filename}

    def response(self, template_name, context):
        self.context.update(context)
        pdf = self.file(self.temp_file_path, template_name, self.context)
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        return response

    def file(self, file_path, template_name, context):
        html = render_to_string(template_name, context)
        options = {
            "enable-local-file-access": True,
            "margin-top": "11mm",
            "margin-bottom": "11mm",
            "margin-left": "11mm",
            "margin-right": "11mm"
        }
        pdfkit.from_string(html, file_path, options=options)
        file = open(file_path, 'rb')
        self.OPENED_FILES.append(file)
        self.OPENED_FILES_PATHS.append(file_path)
        return file

    def merge_files(self, files, output_path):
        pdf_writer = PyPDF2.PdfFileWriter()
        for file in files:
            reader = PyPDF2.PdfFileReader(file)
            for page in reader.pages:
                pdf_writer.addPage(page)

        with open(output_path, 'wb') as out_file:
            pdf_writer.write(out_file)

        out_file = open(output_path, 'rb')
        self.OPENED_FILES_PATHS.append(output_path)
        self.OPENED_FILES.append(out_file)
        return out_file

    def merged_response(self, template_name, contexts_list):
        files = list()
        for t, context in enumerate(contexts_list):
            tmp_file_name = f'{uuid.uuid4().hex}.pdf'
            tmp_file_name = os.path.join(settings.MEDIA_ROOT, tmp_file_name)
            self.context.update(context)
            files.append(self.file(tmp_file_name, template_name, context))
        pdf = self.merge_files(files, self.temp_file_path)
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        return response

    def __del__(self):
        for file in self.OPENED_FILES:
            file.close()
        for file_path in self.OPENED_FILES_PATHS:
            if os.path.exists(file_path):
                os.remove(file_path)
