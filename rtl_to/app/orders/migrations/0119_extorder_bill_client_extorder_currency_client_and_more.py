# Generated by Django 4.1.11 on 2023-09-24 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0118_transit_cargo_handling_transit_packages_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='extorder',
            name='bill_client',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Счет клиента'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='currency_client',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('INR', 'INR')], default='RUB', max_length=3, verbose_name='Валюта заказчика'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='docs_list',
            field=models.TextField(blank=True, null=True, verbose_name='Номера транспортных документов'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='price_client',
            field=models.FloatField(default=0, verbose_name='Ставка заказчика'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='weight_payed',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Оплачиваемый вес'),
        ),
        migrations.AddField(
            model_name='transit',
            name='price_from_eo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Цена продажи'),
        ),
        migrations.AlterField(
            model_name='extorder',
            name='price_carrier',
            field=models.FloatField(default=0, verbose_name='Ставка подрядчика'),
        ),
    ]
