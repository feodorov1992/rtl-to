# Generated by Django 4.0.2 on 2022-09-29 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0020_alter_counterparty_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='counterparty',
            name='admin',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]