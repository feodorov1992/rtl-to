# Generated by Django 4.1.13 on 2024-03-18 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0049_clientcontract_mark_contractorcontract_mark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientcontract',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('INR', 'INR'), ('CNY', 'CNY')], default='RUB', max_length=3, verbose_name='Валюта договора'),
        ),
        migrations.AlterField(
            model_name='contractorcontract',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('INR', 'INR'), ('CNY', 'CNY')], default='RUB', max_length=3, verbose_name='Валюта договора'),
        ),
    ]
