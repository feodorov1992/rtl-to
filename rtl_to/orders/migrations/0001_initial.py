# Generated by Django 4.0.2 on 2022-03-28 09:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_auth', '0003_client_contact_contractor_counterparty_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('client_number', models.CharField(blank=True, max_length=50, verbose_name='Номер заказчика')),
                ('inner_number', models.CharField(blank=True, max_length=50, verbose_name='Внутренний номер')),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('international', 'Международная'), ('internal', 'Внутренняя')], db_index=True, default='internal', max_length=50, verbose_name='Вид поручения')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='Цена поручения')),
                ('price_carrier', models.FloatField(blank=True, null=True, verbose_name='Цена поручения (перевозчика)')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_auth.client', verbose_name='Заказчик')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Менеджер')),
            ],
            options={
                'verbose_name': 'поручение',
                'verbose_name_plural': 'поручения',
                'permissions': [('view_all_orders', 'Can view all orders')],
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(choices=[('new', 'Ожидает обработки'), ('bargain', 'Согласование ставок'), ('pending', 'Обрабатывается перевозчиком'), ('in_progress', 'В пути'), ('completed', 'Выполнено'), ('rejected', 'Отменено')], default='new', max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Статус поручения',
                'verbose_name_plural': 'Статусы поручения',
            },
        ),
        migrations.CreateModel(
            name='Transit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('api_id', models.CharField(blank=True, max_length=255, null=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('volume', models.FloatField(verbose_name='Заявленный объем')),
                ('volume_payed', models.FloatField(verbose_name='Оплачиваемый объем')),
                ('weight', models.FloatField(verbose_name='Заявленный вес брутто')),
                ('weight_payed', models.FloatField(verbose_name='Оплачиваемый вес брутто')),
                ('quantity', models.FloatField(verbose_name='Заявленное количество мест')),
                ('quantity_payed', models.FloatField(verbose_name='Оплачиваемое количество мест')),
                ('value', models.FloatField(verbose_name='Заявленная стоимость')),
                ('from_addr', models.CharField(max_length=255, verbose_name='Адрес отправления')),
                ('to_addr', models.CharField(max_length=255, verbose_name='Адрес доставки')),
                ('type', models.CharField(choices=[('auto', 'Авто'), ('plane', 'Авиа'), ('rail', 'Ж/Д'), ('ship', 'Море')], db_index=True, max_length=50, verbose_name='Вид перевозки')),
                ('price', models.FloatField(verbose_name='Цена перевозки')),
                ('price_carrier', models.FloatField(verbose_name='Цена перевозки (перевозчика)')),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_auth.contractor', verbose_name='Перевозчик')),
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
                ('created_at', models.DateTimeField(auto_created=True, verbose_name='Время')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.transitstatus', verbose_name='Статус')),
                ('transit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.transit', verbose_name='Перевозка')),
            ],
        ),
        migrations.AddField(
            model_name='transit',
            name='status',
            field=models.ForeignKey(default='new', on_delete=django.db.models.deletion.CASCADE, related_name='transits', to='orders.transitstatus', to_field='label', verbose_name='Статус перевозки'),
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, verbose_name='Время')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.order', verbose_name='Поручение')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.orderstatus', verbose_name='Статус')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.ForeignKey(default='new', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.orderstatus', to_field='label', verbose_name='Статус'),
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Наименование груза')),
                ('volume', models.FloatField(verbose_name='Объем')),
                ('weight', models.FloatField(verbose_name='Вес брутто')),
                ('quantity', models.FloatField(verbose_name='Количество мест')),
                ('value', models.FloatField(verbose_name='Заявленная стоимость')),
                ('transit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cargos', to='orders.transit', verbose_name='Перевозка')),
            ],
        ),
    ]
