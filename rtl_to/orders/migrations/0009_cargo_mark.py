# Generated by Django 4.0.2 on 2022-04-05 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_cargo_extra_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='mark',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Маркировка'),
        ),
    ]
