# Generated by Django 4.0.8 on 2023-01-19 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0099_transport'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Transport',
        ),
    ]