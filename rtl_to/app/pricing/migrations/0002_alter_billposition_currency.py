# Generated by Django 4.1.13 on 2024-03-18 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billposition',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('INR', 'INR'), ('CNY', 'CNY')], max_length=3, verbose_name='Валюта'),
        ),
    ]