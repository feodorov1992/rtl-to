# Generated by Django 4.0.2 on 2022-07-22 12:19

import app_auth.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0011_reportparams_report_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('inn', models.CharField(blank=True, db_index=True, max_length=12, null=True, validators=[app_auth.models.inn_validator], verbose_name='ИНН')),
                ('kpp', models.CharField(blank=True, db_index=True, max_length=12, null=True, verbose_name='КПП')),
                ('short_name', models.CharField(max_length=255, verbose_name='Краткое наименование')),
                ('legal_address', models.CharField(max_length=255, verbose_name='Юр. адрес')),
                ('fact_address', models.CharField(max_length=255, verbose_name='Факт. адрес')),
                ('controlled_clients', models.ManyToManyField(to='app_auth.Client', verbose_name='Поднадзорные организации')),
            ],
            options={
                'verbose_name': 'клиент',
                'verbose_name_plural': 'клиенты',
                'permissions': [('view_all_clients', 'Can view all clients')],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='auditor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agents', to='app_auth.auditor', verbose_name='контроллирующий орган'),
        ),
    ]
