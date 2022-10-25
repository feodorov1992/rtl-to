# Generated by Django 4.0.8 on 2022-10-25 16:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0007_alter_docoriginal_doc_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='waybilldata',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='waybilldata',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
