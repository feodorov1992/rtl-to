# Generated by Django 4.1.11 on 2023-09-19 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0116_alter_transit_price_alter_transit_price_currency_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transit',
            name='price_non_rub',
        ),
    ]
