# Generated by Django 4.1.11 on 2023-11-24 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0126_alter_order_client_number_alter_order_inner_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='transit',
            name='price_approval_req_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата отправки ставки на согласование'),
        ),
    ]
