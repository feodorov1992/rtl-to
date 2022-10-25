# Generated by Django 4.0.8 on 2022-10-24 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0078_alter_extorder_date_alter_extorder_status'),
        ('print_forms', '0004_waybilldata_ext_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waybilldata',
            name='ext_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waybills', to='orders.extorder', verbose_name='Исх. поручение'),
        ),
    ]
