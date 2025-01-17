# Generated by Django 4.0.2 on 2022-06-01 11:44

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0005_alter_client_inn_alter_client_kpp_and_more'),
        ('orders', '0026_alter_transit_options_transit_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transit',
            name='creation_date',
        ),
        migrations.RemoveField(
            model_name='transitsegment',
            name='creation_date',
        ),
        migrations.AddField(
            model_name='transitsegment',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='app_auth.client', verbose_name='Заказчик'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='transit',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
