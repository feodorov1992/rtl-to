# Generated by Django 4.0.8 on 2022-10-24 18:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0002_waybilldata_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waybilldata',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
