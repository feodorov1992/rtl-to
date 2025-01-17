# Generated by Django 4.0.2 on 2022-09-28 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0071_remove_autotransit_segment_delete_aerotransit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cargo_name',
            field=models.CharField(default='', max_length=150, verbose_name='Общее наименование груза'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='cargo_origin',
            field=models.CharField(default='Россия', max_length=150, verbose_name='Страна происхождения груза'),
        ),
    ]
