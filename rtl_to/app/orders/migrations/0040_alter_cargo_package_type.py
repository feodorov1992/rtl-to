# Generated by Django 4.0.2 on 2022-06-06 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0039_alter_cargo_package_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='package_type',
            field=models.CharField(choices=[('no_package', 'Без упаковки'), ('envelope', 'Конверт'), ('pile', 'Навалом'), ('cardboard_box', 'Картонная коробка'), ('pallet', 'Паллет'), ('pack', 'Пачка'), ('bag', 'Мешок'), ('big_bag', 'Биг бэг'), ('wooden_box', 'Деревянный ящик'), ('barrel', 'Бочка'), ('roll', 'Рулон'), ('euroocube', 'Еврокуб'), ('coil', 'Катушка'), ('bale', 'Кипа'), ('safe_package', 'Сейф-пакет'), ('package', 'Пакет'), ('container', 'Контейнер')], default='no_package', max_length=255, verbose_name='Тип упаковки'),
        ),
    ]
