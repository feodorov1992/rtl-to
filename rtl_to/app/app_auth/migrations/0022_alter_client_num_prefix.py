# Generated by Django 4.0.8 on 2022-11-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0021_counterparty_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='num_prefix',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Префикс номера поручения'),
        ),
    ]
