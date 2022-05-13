# Generated by Django 4.0.2 on 2022-03-28 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_transit_price_alter_transit_price_carrier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.FloatField(default=0, verbose_name='Цена поручения'),
        ),
        migrations.AlterField(
            model_name='order',
            name='price_carrier',
            field=models.FloatField(default=0, verbose_name='Цена поручения (перевозчика)'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='price',
            field=models.FloatField(default=0, verbose_name='Цена перевозки'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='price_carrier',
            field=models.FloatField(default=0, verbose_name='Цена перевозки (перевозчика)'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='quantity',
            field=models.FloatField(default=0, verbose_name='Заявленное количество мест'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='quantity_payed',
            field=models.FloatField(default=0, verbose_name='Оплачиваемое количество мест'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='value',
            field=models.FloatField(default=0, verbose_name='Заявленная стоимость'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='volume',
            field=models.FloatField(default=0, verbose_name='Заявленный объем'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='volume_payed',
            field=models.FloatField(default=0, verbose_name='Оплачиваемый объем'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='weight',
            field=models.FloatField(default=0, verbose_name='Заявленный вес брутто'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='weight_payed',
            field=models.FloatField(default=0, verbose_name='Оплачиваемый вес брутто'),
        ),
    ]
