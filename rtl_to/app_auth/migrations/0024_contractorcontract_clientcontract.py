# Generated by Django 4.0.8 on 2022-11-18 11:42

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0023_auditor_full_name_auditor_ogrn_client_full_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorContract',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number', models.CharField(max_length=255, verbose_name='№ договора')),
                ('sign_date', models.DateField(verbose_name='Дата заключения договора')),
                ('expiration_date', models.DateField(verbose_name='Дата окончания действия договора')),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='app_auth.contractor', verbose_name='Подрядчик')),
            ],
            options={
                'verbose_name': 'договор с подрядчиком',
                'verbose_name_plural': 'договоры с подрядчиками',
            },
        ),
        migrations.CreateModel(
            name='ClientContract',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number', models.CharField(max_length=255, verbose_name='№ договора')),
                ('sign_date', models.DateField(verbose_name='Дата заключения договора')),
                ('expiration_date', models.DateField(verbose_name='Дата окончания действия договора')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='app_auth.client', verbose_name='Заказчик')),
            ],
            options={
                'verbose_name': 'договор с клиентом',
                'verbose_name_plural': 'договоры с клиентами',
            },
        ),
    ]
