# Generated by Django 4.0.2 on 2022-06-13 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0044_order_order_date_alter_order_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата поручения'),
        ),
    ]
