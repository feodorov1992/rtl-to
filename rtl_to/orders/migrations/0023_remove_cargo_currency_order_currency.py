# Generated by Django 4.0.2 on 2022-05-31 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_remove_cargo_value_remove_transit_insurance_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cargo',
            name='currency',
        ),
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')], default='RUB', max_length=3, verbose_name='Валюта'),
        ),
    ]
