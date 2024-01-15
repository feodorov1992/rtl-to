import uuid

from django.db import models
from django.utils import timezone


class SyncLogEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=True, blank=True, verbose_name='Время создания')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    object_type = models.CharField(max_length=255, db_index=True, verbose_name='Тип объекта')
    node = models.CharField(max_length=255, db_index=True, verbose_name='Имя ноды')
    obj_pk = models.UUIDField(verbose_name='ID объекта')
    obj_last_update = models.DateTimeField(verbose_name='Время последнего изменения объекта')

    class Meta:
        unique_together = 'node', 'object_type', 'obj_pk'
