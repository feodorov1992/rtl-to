# Generated by Django 4.0.2 on 2022-07-22 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0064_order_auditor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='auditor',
            new_name='auditors',
        ),
    ]
