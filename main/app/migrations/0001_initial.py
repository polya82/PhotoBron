import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150, verbose_name='ФИО')),
                ('phone', models.CharField(max_length=20, unique=True, verbose_name='телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='зарегистрирован')),
            ],
            options={
                'verbose_name': 'клиент',
                'verbose_name_plural': 'клиенты',
                'ordering': ('full_name',),
            },
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='название зала')),
                ('capacity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='вместимость, чел.')),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('100.00'))], verbose_name='ставка за час, руб.')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
            ],
            options={
                'verbose_name': 'зал',
                'verbose_name_plural': 'залы',
                'ordering': ('studio', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='название')),
                ('address', models.CharField(max_length=200, verbose_name='адрес')),
                ('contact_phone', models.CharField(max_length=20, verbose_name='контактный телефон')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='студия работает')),
            ],
            options={
                'verbose_name': 'студия',
                'verbose_name_plural': 'студии',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='наименование')),
                ('category', models.CharField(max_length=50, verbose_name='категория')),
                ('hourly_price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='цена аренды за час, руб.')),
            ],
            options={
                'verbose_name': 'оборудование',
                'verbose_name_plural': 'оборудование',
                'ordering': ('category', 'name'),
                'constraints': [models.CheckConstraint(condition=models.Q(('hourly_price__gte', 0)), name='app_equipment_price_positive')],
            },
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='дата')),
                ('start_time', models.TimeField(verbose_name='начало')),
                ('end_time', models.TimeField(verbose_name='конец')),
                ('status', models.CharField(choices=[('open', 'свободно'), ('booked', 'занято')], default='open', max_length=10, verbose_name='статус окна')),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='app.hall', verbose_name='зал')),
            ],
            options={
                'verbose_name': 'слот аренды',
                'verbose_name_plural': 'слоты аренды',
                'ordering': ('date', 'start_time'),
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('planned', 'запланировано'), ('completed', 'проведено'), ('cancelled', 'отменено')], default='planned', max_length=10, verbose_name='статус')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='итоговая стоимость, руб.')),
                ('comment', models.CharField(blank=True, max_length=300, verbose_name='комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создана')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='app.client', verbose_name='клиент')),
                ('slot', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='booking', to='app.slot', verbose_name='слот')),
            ],
            options={
                'verbose_name': 'бронирование',
                'verbose_name_plural': 'бронирования',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='hall',
            name='studio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='halls', to='app.studio', verbose_name='студия'),
        ),
        migrations.CreateModel(
            name='HallEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='количество')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='примечание')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hall_links', to='app.equipment', verbose_name='оборудование')),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hall_equipment', to='app.hall', verbose_name='зал')),
            ],
            options={
                'verbose_name': 'оборудование зала',
                'verbose_name_plural': 'оборудование залов',
                'ordering': ('hall', 'equipment'),
                'constraints': [models.UniqueConstraint(fields=('hall', 'equipment'), name='app_hallequipment_unique'), models.CheckConstraint(condition=models.Q(('quantity__gte', 1), ('quantity__lte', 20)), name='app_hallequipment_quantity_range')],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='сумма, руб.')),
                ('method', models.CharField(choices=[('card', 'карта'), ('cash', 'наличные'), ('transfer', 'перевод')], max_length=10, verbose_name='способ оплаты')),
                ('paid_at', models.DateTimeField(verbose_name='оплачено')),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='app.booking', verbose_name='бронирование')),
            ],
            options={
                'verbose_name': 'оплата',
                'verbose_name_plural': 'оплаты',
                'ordering': ('-paid_at',),
                'constraints': [models.CheckConstraint(condition=models.Q(('amount__gte', 0)), name='app_payment_amount_positive')],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='оценка')),
                ('text', models.TextField(blank=True, verbose_name='текст отзыва')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='app.booking', verbose_name='бронирование')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'ordering': ('-created_at',),
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='app_review_rating_range')],
            },
        ),
        migrations.AddConstraint(
            model_name='slot',
            constraint=models.UniqueConstraint(fields=('hall', 'date', 'start_time'), name='app_slot_unique_window'),
        ),
        migrations.AddConstraint(
            model_name='slot',
            constraint=models.CheckConstraint(condition=models.Q(('start_time__lt', models.F('end_time'))), name='app_slot_time_order'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('total_price__gte', 0)), name='app_booking_total_positive'),
        ),
        migrations.AddConstraint(
            model_name='hall',
            constraint=models.UniqueConstraint(fields=('studio', 'name'), name='app_hall_unique_in_studio'),
        ),
        migrations.AddConstraint(
            model_name='hall',
            constraint=models.CheckConstraint(condition=models.Q(('capacity__gte', 1), ('capacity__lte', 50)), name='app_hall_capacity_range'),
        ),
        migrations.AddConstraint(
            model_name='hall',
            constraint=models.CheckConstraint(condition=models.Q(('hourly_rate__gte', 100)), name='app_hall_rate_positive'),
        ),
    ]
