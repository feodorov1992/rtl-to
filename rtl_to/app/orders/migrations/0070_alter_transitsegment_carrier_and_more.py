# Generated by Django 4.0.2 on 2022-09-19 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0020_alter_counterparty_client_and_more'),
        ('orders', '0069_alter_aerotransit_options_alter_autotransit_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transitsegment',
            name='carrier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='app_auth.contractor', verbose_name='Перевозчик'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='currency',
            field=models.CharField(blank=True, choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')], default='RUB', max_length=3, null=True, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='price',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Ставка'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='price_carrier',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Закупочная цена'),
        ),
    ]
