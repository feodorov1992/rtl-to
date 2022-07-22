# Generated by Django 4.0.2 on 2022-07-21 14:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0062_alter_cargo_created_at_alter_transit_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
    ]
