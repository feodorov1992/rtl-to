# Generated by Django 4.0.8 on 2022-11-17 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0027_alter_clientcontract_id_alter_clientcontract_u_id_and_more'),
        ('orders', '0088_extorder_contract_order_contract'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientcontract',
            name='id',
        ),
        migrations.RemoveField(
            model_name='contractorcontract',
            name='id',
        ),
    ]