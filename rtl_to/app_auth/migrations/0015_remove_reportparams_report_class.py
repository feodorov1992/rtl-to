# Generated by Django 4.0.2 on 2022-07-29 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0014_remove_reportparams__fields_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportparams',
            name='report_class',
        ),
    ]
