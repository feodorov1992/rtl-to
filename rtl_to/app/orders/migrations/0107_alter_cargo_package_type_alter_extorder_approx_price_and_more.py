# Generated by Django 4.1.10 on 2023-08-03 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0106_extorder_approx_price_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='package_type',
            field=models.CharField(choices=[('wooden_box', 'Деревянный ящик'), ('cardboard_box', 'Картонная коробка'), ('no_package', 'Без упаковки'), ('envelope', 'Конверт'), ('container', 'Контейнер'), ('package', 'Пакет'), ('pallet', 'Паллет'), ('bag', 'Мешок'), ('barrel', 'Бочка'), ('bucket', 'Ведро'), ('roll', 'Рулон'), ('pile', 'Навалом'), ('pack', 'Пачка'), ('big_bag', 'Биг бэг'), ('euroocube', 'Еврокуб'), ('coil', 'Катушка'), ('bale', 'Кипа'), ('safe_package', 'Сейф-пакет'), ('bubble_wrap', 'Пленка пузырчатая'), ('stretch_film', 'Пленка стрейч'), ('tin_can', 'Банка жестяная'), ('glass_can', 'Банка стеклянная'), ('cont_metal', 'Контейнер металлический'), ('cont_wood', 'Контейнер деревянный'), ('cont_plast', 'Контейнер пластиковый'), ('bundle', 'Связка'), ('canister', 'Канистра')], default='wooden_box', max_length=255, verbose_name='Тип упаковки'),
        ),
        migrations.AlterField(
            model_name='extorder',
            name='approx_price',
            field=models.FloatField(default=0, verbose_name='Ориентировочная цена'),
        ),
        migrations.AlterField(
            model_name='transit',
            name='value',
            field=models.FloatField(blank=True, default=1, null=True, verbose_name='Заявленная стоимость'),
        ),
    ]
