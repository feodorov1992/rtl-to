# Generated by Django 4.0.2 on 2022-05-16 07:38

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderhistory',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterModelOptions(
            name='transithistory',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 16, 7, 38, 22, 428433, tzinfo=utc), verbose_name='Время'),
        ),
        migrations.AlterField(
            model_name='transithistory',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 16, 7, 38, 22, 428433, tzinfo=utc), verbose_name='Время'),
        ),
    ]
