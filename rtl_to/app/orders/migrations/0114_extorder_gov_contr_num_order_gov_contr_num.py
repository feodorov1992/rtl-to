# Generated by Django 4.1.11 on 2023-09-17 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0113_transit_docs_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='extorder',
            name='gov_contr_num',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='№ ИГК'),
        ),
        migrations.AddField(
            model_name='order',
            name='gov_contr_num',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='№ ИГК'),
        ),
    ]
