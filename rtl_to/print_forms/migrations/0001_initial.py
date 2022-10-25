# Generated by Django 4.0.8 on 2022-10-25 16:50

from django.db import migrations, models
import django.db.models.deletion
import print_forms.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0078_alter_extorder_date_alter_extorder_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocOriginal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('doc_type', models.CharField(choices=[('auto', 'ТН'), ('plane', 'AWB'), ('rail', 'СМГС'), ('ship', 'Коносамент')], max_length=50, verbose_name='Тип документа')),
                ('doc_number', models.CharField(max_length=100, unique=True, verbose_name='Номер')),
                ('doc_date', models.DateField(verbose_name='Дата документа')),
                ('quantity', models.IntegerField(default=0, verbose_name='Количество мест')),
                ('weight_payed', models.FloatField(default=0, verbose_name='Оплачиваемый вес')),
                ('load_date', models.DateField(verbose_name='Дата погрузки')),
                ('file', models.FileField(upload_to=print_forms.models.path_by_order, verbose_name='Скан документа')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='originals', to='orders.transitsegment', verbose_name='Плечо перевозки')),
                ('transit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='originals', to='orders.transit', verbose_name='Перевозка')),
            ],
        ),
        migrations.CreateModel(
            name='WaybillData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('waybill_number', models.CharField(max_length=100, unique=True, verbose_name='Номер ТН')),
                ('waybill_date', models.DateField(verbose_name='Дата накладной')),
                ('file_name', models.CharField(max_length=100, verbose_name='Имя файла')),
                ('driver_last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('driver_first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('driver_second_name', models.CharField(max_length=50, verbose_name='Отчество')),
                ('driver_license', models.CharField(max_length=50, verbose_name='Номер в.у.')),
                ('driver_entity', models.CharField(default='РФ', max_length=50, verbose_name='Национальность')),
                ('auto_model', models.CharField(max_length=100, verbose_name='Марка авто')),
                ('auto_number', models.CharField(max_length=20, verbose_name='Гос. номер')),
                ('ownership', models.CharField(choices=[('own', 'Собственность'), ('family', 'Совместная собственность супругов'), ('rent', 'Аренда'), ('leasing', 'Лизинг'), ('free', 'Безвозмездное пользование')], default='own', max_length=20, verbose_name='Тип владения')),
                ('ext_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waybills', to='orders.extorder', verbose_name='Исх. поручение')),
                ('original', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waybill', to='print_forms.docoriginal', verbose_name='Оригинал документа')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waybills', to='orders.transitsegment', verbose_name='Плечо перевозки')),
            ],
        ),
    ]
