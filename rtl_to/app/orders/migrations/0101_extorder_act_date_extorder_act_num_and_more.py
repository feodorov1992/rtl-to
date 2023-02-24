# Generated by Django 4.1.7 on 2023-02-23 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0100_delete_transport'),
    ]

    operations = [
        migrations.AddField(
            model_name='extorder',
            name='act_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата акта'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='act_num',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Акт №'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='bill_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата счета'),
        ),
        migrations.AddField(
            model_name='extorder',
            name='bill_num',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Счет №'),
        ),
    ]
