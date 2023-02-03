# Generated by Django 4.0.2 on 2022-05-25 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_remove_transit_carrier_remove_transit_contract_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')], default='RUB', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'Новое'), ('pre_process', 'Принято в работу'), ('rejected', 'Аннулировано'), ('in_progress', 'На исполнении'), ('delivered', 'Выполнено'), ('bargain', 'Согласование ставок'), ('completed', 'Завершено')], db_index=True, max_length=50, null=True, verbose_name='Статус поручения'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='status',
            field=models.CharField(choices=[('new', 'Новое'), ('pre_process', 'Принято в работу'), ('rejected', 'Аннулировано'), ('in_progress', 'На исполнении'), ('delivered', 'Выполнено'), ('bargain', 'Согласование ставок'), ('completed', 'Завершено')], default='new', max_length=50, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')], default='RUB', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='status',
            field=models.CharField(blank=True, choices=[('carrier_select', 'Выбор перевозчика'), ('pickup', 'Забор груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], db_index=True, max_length=50, null=True, verbose_name='Статус перевозки'),
        ),
        migrations.AlterField(
            model_name='transithistory',
            name='status',
            field=models.CharField(choices=[('carrier_select', 'Выбор перевозчика'), ('pickup', 'Забор груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], default='carrier_select', max_length=50, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='currency',
            field=models.CharField(choices=[('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')], default='RUB', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='transitsegment',
            name='status',
            field=models.CharField(choices=[('waiting', 'В ожидании'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Аннулировано')], db_index=True, default='waiting', max_length=50, verbose_name='Статус перевозки'),
        ),
        migrations.AlterField(
            model_name='transitstatus',
            name='label',
            field=models.CharField(choices=[('carrier_select', 'Выбор перевозчика'), ('pickup', 'Забор груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], default='carrier_select', max_length=50, unique=True),
        ),
    ]
