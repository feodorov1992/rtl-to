# Generated by Django 4.0.2 on 2022-06-17 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0054_alter_order_insurance_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='value',
            field=models.FloatField(blank=True, default=0, verbose_name='Заявленная стоимость'),
        ),
    ]
