# Generated by Django 4.0.2 on 2022-07-05 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0056_alter_order_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='from_addr_forlist',
            field=models.TextField(editable=False, verbose_name='Адрес забора груза'),
        ),
        migrations.AlterField(
            model_name='order',
            name='to_addr_forlist',
            field=models.TextField(editable=False, verbose_name='Адрес доставки'),
        ),
    ]
