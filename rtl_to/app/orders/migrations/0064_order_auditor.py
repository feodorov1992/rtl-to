# Generated by Django 4.0.2 on 2022-07-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_auth', '0012_auditor_user_auditor'),
        ('orders', '0063_alter_order_created_at_alter_order_last_update_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='auditor',
            field=models.ManyToManyField(related_name='orders', to='app_auth.Auditor', verbose_name='Аудиторы'),
        ),
    ]