# Generated by Django 4.1.10 on 2023-09-04 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0109_order_re_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='extorder',
            name='insurance_detail',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Инф. по страхованию (для бланка ПЭ)'),
        ),
    ]
