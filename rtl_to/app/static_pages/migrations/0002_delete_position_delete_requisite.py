# Generated by Django 4.0.2 on 2022-05-20 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_pages', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Position',
        ),
        migrations.DeleteModel(
            name='Requisite',
        ),
    ]
