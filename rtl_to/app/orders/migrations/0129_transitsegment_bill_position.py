# Generated by Django 4.1.13 on 2024-01-06 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0001_initial'),
        ('orders', '0128_extorder_insurance_currency_extorder_insurance_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='transitsegment',
            name='bill_position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pricing.billposition'),
        ),
    ]