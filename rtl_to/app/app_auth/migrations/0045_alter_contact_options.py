# Generated by Django 4.1.13 on 2024-01-10 00:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0044_alter_client_order_label_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'контакт', 'verbose_name_plural': 'контакты'},
        ),
    ]
