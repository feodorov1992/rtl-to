# Generated by Django 4.1.10 on 2023-09-04 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0035_user_boss'),
    ]

    operations = [
        migrations.AddField(
            model_name='currencyrate',
            name='INR',
            field=models.FloatField(default=0, editable=False, verbose_name='INR'),
            preserve_default=False,
        ),
    ]
