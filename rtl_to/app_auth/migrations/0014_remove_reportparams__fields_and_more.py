# Generated by Django 4.0.2 on 2022-07-27 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0013_alter_auditor_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportparams',
            name='_fields',
        ),
        migrations.AddField(
            model_name='reportparams',
            name='_order_fields',
            field=models.TextField(default='', verbose_name='Поля поручения'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportparams',
            name='_segment_fields',
            field=models.TextField(default='', verbose_name='Поля плеча перевозки'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportparams',
            name='_transit_fields',
            field=models.TextField(default='', verbose_name='Поля перевозки'),
            preserve_default=False,
        ),
    ]