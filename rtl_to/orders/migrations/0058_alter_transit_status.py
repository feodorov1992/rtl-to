# Generated by Django 4.0.2 on 2022-07-05 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0057_alter_order_from_addr_forlist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transit',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('carrier_select', 'Первичная обработка'), ('pickup', 'Забор груза'), ('in_progress', 'В пути'), ('temporary_storage', 'Груз на СВХ (ТО)'), ('transit_storage', 'Груз на транзитном складе'), ('completed', 'Доставлено'), ('rejected', 'Аннулировано')], db_index=True, default='new', max_length=50, verbose_name='Статус перевозки'),
        ),
    ]