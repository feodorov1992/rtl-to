# Generated by Django 4.1.10 on 2023-07-31 20:25

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0032_clientcontract_currency_clientcontract_current_sum_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField(default=django.utils.timezone.now, editable=False, verbose_name='Дата курса')),
                ('EUR', models.FloatField(editable=False, verbose_name='EUR')),
                ('USD', models.FloatField(editable=False, verbose_name='USD')),
                ('GBP', models.FloatField(editable=False, verbose_name='GBP')),
            ],
        ),
    ]