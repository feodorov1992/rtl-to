# Generated by Django 4.0.2 on 2022-05-31 07:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0003_alter_client_num_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='contract',
            field=models.CharField(default='', max_length=255, verbose_name='№ договора'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='contract_expiration_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата окончания действия договора'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='contract_sign_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата заключения договора'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contractor',
            name='contract',
            field=models.CharField(default='', max_length=255, verbose_name='№ договора'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contractor',
            name='contract_expiration_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата окончания действия договора'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contractor',
            name='contract_sign_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата заключения договора'),
            preserve_default=False,
        ),
    ]
