# Generated by Django 4.0.2 on 2022-04-13 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_rename_wight_volume_transit_weight_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='transit',
            name='sub_number',
            field=models.CharField(db_index=True, default=1, max_length=255),
        ),
    ]
