# Generated by Django 4.0.2 on 2022-06-17 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0052_alter_order_insurance_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='quantity',
            field=models.IntegerField(default=0, verbose_name='Кол-во мест'),
        ),
    ]
