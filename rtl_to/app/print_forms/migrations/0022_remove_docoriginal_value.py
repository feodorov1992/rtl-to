# Generated by Django 4.1.10 on 2023-08-23 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0021_transdocsdata_auto_tonnage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='docoriginal',
            name='value',
        ),
    ]
