# Generated by Django 4.0.2 on 2022-07-15 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0008_alter_client_inn_alter_client_kpp_remove_contact_cp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='cp',
            field=models.ManyToManyField(related_name='contacts', to='app_auth.Counterparty', verbose_name='Контрагенты'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(max_length=30, verbose_name='Тел.'),
        ),
    ]
