# Generated by Django 4.0.8 on 2022-11-16 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0005_transdocsdata_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='docoriginal',
            name='value',
            field=models.FloatField(default=0, verbose_name='Стоимость'),
        ),
    ]
