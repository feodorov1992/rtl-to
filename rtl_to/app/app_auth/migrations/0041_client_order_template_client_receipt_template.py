# Generated by Django 4.1.13 on 2023-12-04 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0040_clientcontract_order_template_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='order_template',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Шаблон ПЭ'),
        ),
        migrations.AddField(
            model_name='client',
            name='receipt_template',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Шаблон ЭР'),
        ),
    ]