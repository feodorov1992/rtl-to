from django.core.management.base import BaseCommand, CommandError
from orders.models import Document, path_by_order
from django.conf import settings
import os


class Command(BaseCommand):
    MEDIA_ROOT = settings.MEDIA_ROOT

    def __init__(self, queryset=None):
        super(Command, self).__init__()
        self.queryset = queryset if queryset else Document.objects.all()

    def parse_paths(self, relative_path):
        rel_path, filename = os.path.split(relative_path)
        abs_path = os.path.join(self.MEDIA_ROOT, rel_path)
        return abs_path, rel_path, filename

    def handle(self, *args, **options):
        for doc in self.queryset:
            old_abs, old_rel, fn = self.parse_paths(doc.file.name)
            new_abs, new_rel, _ = self.parse_paths(
                path_by_order(doc, fn, month=doc.order.created_at.month, year=doc.order.created_at.year)
            )
            old_abs_full = os.path.join(old_abs, fn)
            new_abs_full = os.path.join(new_abs, fn)
            new_rel_full = os.path.join(new_rel, fn)
            if doc.file.name != new_rel_full:
                doc.file.name = new_rel_full
                doc.save()
                os.makedirs(new_abs, exist_ok=True)
                os.rename(old_abs_full, new_abs_full)
                os.remove(old_abs)
