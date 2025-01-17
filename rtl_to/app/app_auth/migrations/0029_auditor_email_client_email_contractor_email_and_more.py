# Generated by Django 4.1.7 on 2023-04-18 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0028_contractor_accountant_contractor_head'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditor',
            name='email',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Почта для рассылки'),
        ),
        migrations.AddField(
            model_name='client',
            name='email',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Почта для рассылки'),
        ),
        migrations.AddField(
            model_name='contractor',
            name='email',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Почта для рассылки'),
        ),
        migrations.AddField(
            model_name='counterparty',
            name='email',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Почта для рассылки'),
        ),
    ]
