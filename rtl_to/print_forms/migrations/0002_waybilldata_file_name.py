# Generated by Django 4.0.8 on 2022-10-24 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='waybilldata',
            name='file_name',
            field=models.CharField(default='', max_length=100, verbose_name='Имя файла'),
            preserve_default=False,
        ),
    ]
