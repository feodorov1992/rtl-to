# Generated by Django 4.1.10 on 2023-08-23 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0108_extorder_currency_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='re_submission',
            field=models.BooleanField(default=False, verbose_name='Перевыставление'),
        ),
    ]
