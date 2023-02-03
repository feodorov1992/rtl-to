# Generated by Django 4.0.8 on 2022-12-05 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0089_alter_order_type_alter_transitsegment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='bill_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер счета'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('carrier_select', 'Первичная обработка'), ('pickup', 'Ожидание забора груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], db_index=True, default='new', max_length=50, verbose_name='Статус перевозки'),
        ),
        migrations.AlterField(
            model_name='transithistory',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('carrier_select', 'Первичная обработка'), ('pickup', 'Ожидание забора груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], default='new', max_length=50, verbose_name='Статус'),
        ),
    ]