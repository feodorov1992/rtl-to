# Generated by Django 4.1.11 on 2023-10-04 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0121_alter_extorder_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='package_type',
            field=models.CharField(choices=[('wooden_box', 'Деревянный ящик'), ('cardboard_box', 'Картонный короб'), ('no_package', 'Без упаковки'), ('envelope', 'Конверт'), ('container', 'Контейнер'), ('package', 'Пакет'), ('pallet', 'Паллет'), ('bag', 'Мешок'), ('barrel', 'Бочка'), ('bucket', 'Ведро'), ('roll', 'Рулон'), ('pile', 'Навалом'), ('pack', 'Пачка'), ('big_bag', 'Биг бэг'), ('euroocube', 'Еврокуб'), ('coil', 'Катушка'), ('bale', 'Кипа'), ('safe_package', 'Сейф-пакет'), ('bubble_wrap', 'Пленка пузырчатая'), ('stretch_film', 'Пленка стрейч'), ('tin_can', 'Банка жестяная'), ('glass_can', 'Банка стеклянная'), ('cont_metal', 'Контейнер металлический'), ('cont_wood', 'Контейнер деревянный'), ('cont_plast', 'Контейнер пластиковый'), ('bundle', 'Связка'), ('canister', 'Канистра'), ('special', 'Специальная упаковка')], default='wooden_box', max_length=255, verbose_name='Тип упаковки'),
        ),
    ]
