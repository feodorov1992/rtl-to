# Generated by Django 4.0.2 on 2022-07-20 16:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0061_alter_transit_receiver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Создано'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
        ),
    ]
