# Generated by Django 4.0.2 on 2022-06-01 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_alter_order_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='transit',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')], default='RUB', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='transit',
            name='value',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Заявленная стоимость'),
        ),
    ]