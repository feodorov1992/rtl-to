# Generated by Django 4.0.8 on 2022-12-06 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0093_remove_order_bill_number_transit_bill_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='transit',
            name='weight_payed',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Оплачиваемый вес'),
        ),
    ]