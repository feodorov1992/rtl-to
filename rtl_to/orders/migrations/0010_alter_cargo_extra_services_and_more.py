# Generated by Django 4.0.2 on 2022-04-05 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_cargo_mark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='extra_services',
            field=models.ManyToManyField(blank=True, to='orders.ExtraService', verbose_name='Доп. услуги'),
        ),
        migrations.AlterField(
            model_name='extraservice',
            name='human_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='extraservice',
            name='machine_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
