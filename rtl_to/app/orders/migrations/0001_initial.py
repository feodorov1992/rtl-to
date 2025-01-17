# Generated by Django 4.0.2 on 2022-05-13 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraCargoParams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.CharField(max_length=100, unique=True)),
                ('human_name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'доп. параметр груза',
                'verbose_name_plural': 'доп. параметры груза',
            },
        ),
        migrations.CreateModel(
            name='ExtraService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.CharField(max_length=100, unique=True)),
                ('human_name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'доп. услуга',
                'verbose_name_plural': 'доп. услуги',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('client_number', models.CharField(blank=True, max_length=50, verbose_name='Номер заказчика')),
                ('inner_number', models.CharField(blank=True, max_length=50, verbose_name='Внутренний номер')),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('international', 'Международная'), ('internal', 'Внутрироссийская')], db_index=True, default='internal', max_length=50, verbose_name='Вид поручения')),
                ('status', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], db_index=True, default='new', max_length=50, verbose_name='Статус поручения')),
                ('price', models.FloatField(default=0, verbose_name='Ставка')),
                ('price_carrier', models.FloatField(default=0, verbose_name='Закупочная цена поручения')),
                ('from_addr_forlist', models.CharField(editable=False, max_length=255, verbose_name='Адрес забора груза')),
                ('to_addr_forlist', models.CharField(editable=False, max_length=255, verbose_name='Адрес доставки')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Примечания')),
                ('from_date_plan', models.DateField(blank=True, null=True, verbose_name='Плановая дата забора груза')),
                ('from_date_fact', models.DateField(blank=True, null=True, verbose_name='Фактическая дата забора груза')),
                ('to_date_plan', models.DateField(blank=True, null=True, verbose_name='Плановая дата доставки')),
                ('to_date_fact', models.DateField(blank=True, null=True, verbose_name='Фактическая дата доставки')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_auth.client', verbose_name='Заказчик')),
                ('client_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_orders_client', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник заказчика')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_orders_manager', to=settings.AUTH_USER_MODEL, verbose_name='Менеджер')),
            ],
            options={
                'verbose_name': 'поручение',
                'verbose_name_plural': 'поручения',
                'permissions': [('view_all_orders', 'Can view all orders')],
            },
        ),
        migrations.CreateModel(
            name='Transit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sub_number', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Субномер')),
                ('api_id', models.CharField(blank=True, max_length=255, null=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('volume', models.FloatField(default=0, verbose_name='Объем')),
                ('weight', models.FloatField(default=0, verbose_name='Вес брутто')),
                ('weight_payed', models.FloatField(default=0, verbose_name='Оплачиваемый вес')),
                ('quantity', models.FloatField(default=0, verbose_name='Количество мест')),
                ('value', models.FloatField(default=0, verbose_name='Заявленная стоимость')),
                ('from_addr', models.CharField(max_length=255, verbose_name='Адрес забора груза')),
                ('from_org', models.CharField(max_length=255, verbose_name='Отправитель')),
                ('from_inn', models.CharField(max_length=255, verbose_name='ИНН отправителя')),
                ('from_contact_name', models.CharField(max_length=255, verbose_name='Контактное лицо')),
                ('from_contact_phone', models.CharField(max_length=255, verbose_name='Телефон')),
                ('from_contact_email', models.CharField(max_length=255, verbose_name='email')),
                ('from_date_plan', models.DateField(blank=True, null=True, verbose_name='Плановая дата забора груза')),
                ('from_date_fact', models.DateField(blank=True, null=True, verbose_name='Фактическая дата забора груза')),
                ('to_addr', models.CharField(max_length=255, verbose_name='Адрес доставки')),
                ('to_org', models.CharField(max_length=255, verbose_name='Получатель')),
                ('to_inn', models.CharField(max_length=255, verbose_name='ИНН получателя')),
                ('to_contact_name', models.CharField(max_length=255, verbose_name='Контактное лицо')),
                ('to_contact_phone', models.CharField(max_length=255, verbose_name='Телефон')),
                ('to_contact_email', models.CharField(max_length=255, verbose_name='email')),
                ('to_date_plan', models.DateField(blank=True, null=True, verbose_name='Плановая дата доставки')),
                ('to_date_fact', models.DateField(blank=True, null=True, verbose_name='Фактическая дата доставки')),
                ('type', models.CharField(choices=[('auto', 'Авто'), ('plane', 'Авиа'), ('rail', 'Ж/Д'), ('ship', 'Море')], db_index=True, max_length=50, verbose_name='Вид перевозки')),
                ('price', models.FloatField(default=0, verbose_name='Цена перевозки')),
                ('price_carrier', models.FloatField(default=0, verbose_name='Цена перевозки (перевозчика)')),
                ('status', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], db_index=True, default='new', max_length=50, verbose_name='Статус перевозки')),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_auth.contractor', verbose_name='Перевозчик')),
                ('extra_services', models.ManyToManyField(blank=True, to='orders.ExtraService', verbose_name='Доп. услуги')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transits', to='orders.order', verbose_name='Поручение')),
            ],
            options={
                'verbose_name': 'перевозка',
                'verbose_name_plural': 'перевозки',
                'permissions': [('view_all_transits', 'Can view all transits')],
            },
        ),
        migrations.CreateModel(
            name='TransitStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], default='new', max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Статус перевозки',
                'verbose_name_plural': 'Статусы перевозки',
            },
        ),
        migrations.CreateModel(
            name='TransitHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], default='new', max_length=50, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время')),
                ('transit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.transit', verbose_name='Перевозка')),
            ],
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, verbose_name='Время')),
                ('status', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], default='new', max_length=50, verbose_name='Статус')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.order', verbose_name='Поручение')),
            ],
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Наименование груза')),
                ('package_type', models.CharField(choices=[('cardboard_box', 'Картонная коробка'), ('wooden_box', 'Деревянный ящик'), ('safe_package', 'Сейф-пакет'), ('package', 'Пакет')], default='cardboard_box', max_length=255, verbose_name='Тип упаковки')),
                ('length', models.FloatField(default=0, verbose_name='Длина')),
                ('width', models.FloatField(default=0, verbose_name='Ширина')),
                ('height', models.FloatField(default=0, verbose_name='Высота')),
                ('weight', models.FloatField(default=0, verbose_name='Вес')),
                ('quantity', models.IntegerField(default=1, verbose_name='Мест')),
                ('value', models.FloatField(default=0, verbose_name='Заявленная стоимость')),
                ('currency', models.CharField(choices=[('RUB', 'Рубль'), ('USD', 'Доллар США'), ('EUR', 'Евро')], default='RUB', max_length=3, verbose_name='Валюта')),
                ('volume_weight', models.FloatField(default=0, verbose_name='Объемный вес')),
                ('mark', models.CharField(blank=True, max_length=255, null=True, verbose_name='Маркировка')),
                ('extra_params', models.ManyToManyField(blank=True, to='orders.ExtraCargoParams', verbose_name='Доп. параметры')),
                ('transit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cargos', to='orders.transit', verbose_name='Перевозка')),
            ],
        ),
    ]
