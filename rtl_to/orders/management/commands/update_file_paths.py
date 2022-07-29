from django.core.management.base import BaseCommand, CommandError
from orders.models import Document, path_by_order
from django.conf import settings
import os


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__()
        self.queryset = queryset if queryset else Document.objects.all()
        self.reports_folder = os.path.join(settings.MEDIA_ROOT, 'reports')
        self.report_filename = 'updated_files.csv'
        self.__init_report()

    @staticmethod
    def __files_sort_key(fn):
        split = fn.split('.')
        if len(split) > 2:
            return int(split[1])
        else:
            return 0

    def __init_report(self):
        os.makedirs(self.reports_folder, exist_ok=True)
        if self.report_filename in os.listdir(self.reports_folder):
            for filename in reversed(sorted(os.listdir(self.reports_folder), key=self.__files_sort_key)):
                if filename == self.report_filename:
                    prefix, suffix = filename.split('.')
                    number = 1
                else:
                    prefix, number, suffix = filename.split('.')
                    number = int(number)
                    number += 1

                if number >= 20:
                    os.remove(os.path.join(self.reports_folder, filename))
                else:
                    os.rename(
                        os.path.join(self.reports_folder, filename),
                        os.path.join(self.reports_folder, '{}.{}.{}'.format(prefix, number, suffix))
                    )
        with open(os.path.join(self.reports_folder, self.report_filename), 'a+') as file:
            file.write('pk,filename,old_path,new_path,where\n')

    def __update_report(self, pk, filename, old_path, new_path):
        old = os.path.exists(os.path.join(settings.MEDIA_ROOT, old_path))
        new = os.path.exists(os.path.join(settings.MEDIA_ROOT, new_path))
        if old and not new:
            where = 'old'
        elif new and not old:
            where = 'new'
        elif new and old:
            where = 'both'
        else:
            where = 'nowhere'

        with open(os.path.join(self.reports_folder, self.report_filename), 'a+') as file:
            file.write('{},{},{},{},{}\n'.format(pk, filename, old_path, new_path, where))

    @staticmethod
    def parse_paths(relative_path):
        rel_path, filename = os.path.split(relative_path)
        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        return abs_path, rel_path, filename

    def handle(self, *args, **options):
        delete_folders = set()
        for doc in self.queryset:
            old_abs, old_rel, fn = self.parse_paths(doc.file.name)
            new_abs, new_rel, _ = self.parse_paths(
                path_by_order(doc, fn, month=doc.order.created_at.month, year=doc.order.created_at.year)
            )
            old_rel_full = os.path.join(old_rel, fn)
            old_abs_full = os.path.join(old_abs, fn)
            new_rel_full = os.path.join(new_rel, fn)
            new_abs_full = os.path.join(new_abs, fn)

            if doc.file.name != new_rel_full:
                os.makedirs(new_abs, exist_ok=True)
                os.rename(old_abs_full, new_abs_full)
                if os.listdir(old_abs):
                    delete_folders.add(old_abs)
                doc.file.name = new_rel_full
                doc.save()

            self.__update_report(doc.pk, doc.file.name, old_rel_full, new_rel_full)

            for folder in delete_folders:
                os.rmdir(folder)
