# Generated by Django 4.1.9 on 2023-06-08 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0030_alter_auditor_email_alter_client_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditor',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Почта для рассылки'),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Почта для рассылки'),
        ),
        migrations.AlterField(
            model_name='contractor',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Почта для рассылки'),
        ),
        migrations.AlterField(
            model_name='counterparty',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Почта для рассылки'),
        ),
    ]
