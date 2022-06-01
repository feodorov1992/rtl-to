# Generated by Django 4.0.2 on 2022-06-01 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0004_client_contract_client_contract_expiration_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='inn',
            field=models.BigIntegerField(db_index=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='client',
            name='kpp',
            field=models.BigIntegerField(db_index=True, verbose_name='КПП'),
        ),
        migrations.AlterField(
            model_name='contractor',
            name='inn',
            field=models.BigIntegerField(db_index=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='contractor',
            name='kpp',
            field=models.BigIntegerField(db_index=True, verbose_name='КПП'),
        ),
        migrations.AlterField(
            model_name='counterparty',
            name='inn',
            field=models.BigIntegerField(db_index=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='counterparty',
            name='kpp',
            field=models.BigIntegerField(db_index=True, verbose_name='КПП'),
        ),
    ]
