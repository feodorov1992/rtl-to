# Generated by Django 4.0.2 on 2022-05-16 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_contract'),
    ]

    operations = [
        migrations.AddField(
            model_name='transit',
            name='contract',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Договор'),
        ),
    ]
