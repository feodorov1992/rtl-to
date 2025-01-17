# Generated by Django 4.0.2 on 2022-06-14 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0045_alter_order_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='client_employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_orders_client', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник заказчика'),
        ),
        migrations.AlterField(
            model_name='order',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_orders_manager', to=settings.AUTH_USER_MODEL, verbose_name='Менеджер'),
        ),
    ]
