# Generated by Django 4.0.8 on 2023-01-19 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0011_transdocsdata_race_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transdocsdata',
            name='race_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Номер отправления (рейса)'),
        ),
    ]
