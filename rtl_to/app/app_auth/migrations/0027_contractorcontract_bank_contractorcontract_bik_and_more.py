# Generated by Django 4.1.7 on 2023-02-24 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0026_remove_reportparams_merge_segments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractorcontract',
            name='bank',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Банк'),
        ),
        migrations.AddField(
            model_name='contractorcontract',
            name='bik',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='БИК банка'),
        ),
        migrations.AddField(
            model_name='contractorcontract',
            name='corr_acc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='к/с'),
        ),
        migrations.AddField(
            model_name='contractorcontract',
            name='pay_acc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='р/с'),
        ),
    ]
