# Generated by Django 4.1.9 on 2023-06-13 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_forms', '0014_alter_transdocsdata_driver_entity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docoriginal',
            name='doc_number',
            field=models.CharField(max_length=100, verbose_name='Номер'),
        ),
    ]