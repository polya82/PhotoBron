from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


def db_check(condition, name):
    try:
        return models.CheckConstraint(condition=condition, name=name)
    except TypeError:
        return models.CheckConstraint(check=condition, name=name)


class Studio(models.Model):
    name = models.CharField("название", max_length=120, unique=True)
    address = models.CharField("адрес", max_length=200)
    contact_phone = models.CharField("контактный телефон", max_length=20)
    description = models.TextField("описание", blank=True)
    is_active = models.BooleanField("студия работает", default=True)

    class Meta:
        verbose_name = "студия"
        verbose_name_plural = "студии"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Hall(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE,
                               related_name="halls", verbose_name="студия")
    name = models.CharField("название зала", max_length=120)
    capacity = models.PositiveSmallIntegerField("вместимость, чел.",
                                                validators=[MinValueValidator(1), MaxValueValidator(50)])
    hourly_rate = models.DecimalField("ставка за час, руб.", max_digits=8, decimal_places=2,
                                      validators=[MinValueValidator(Decimal("100.00"))])
    description = models.TextField("описание", blank=True)

    class Meta:
        verbose_name = "зал"
        verbose_name_plural = "залы"
        ordering = ("studio", "name")
        constraints = [
            models.UniqueConstraint(fields=("studio", "name"), name="app_hall_unique_in_studio"),
            db_check(models.Q(capacity__gte=1, capacity__lte=50), "app_hall_capacity_range"),
            db_check(models.Q(hourly_rate__gte=100), "app_hall_rate_positive"),
        ]

    def __str__(self):
        return f"{self.studio.name} — {self.name}"


class Client(models.Model):
    full_name = models.CharField("ФИО", max_length=150)
    phone = models.CharField("телефон", max_length=20, unique=True)
    email = models.EmailField("email", blank=True)
    created_at = models.DateTimeField("зарегистрирован", auto_now_add=True)

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        ordering = ("full_name",)

    def __str__(self):
        return self.full_name


class Equipment(models.Model):
    name = models.CharField("наименование", max_length=150, unique=True)
    category = models.CharField("категория", max_length=50)
    hourly_price = models.DecimalField("цена аренды за час, руб.", max_digits=8, decimal_places=2,
                                       validators=[MinValueValidator(Decimal("0.01"))])

    class Meta:
        verbose_name = "оборудование"
        verbose_name_plural = "оборудование"
        ordering = ("category", "name")
        constraints = [
            db_check(models.Q(hourly_price__gte=0), "app_equipment_price_positive"),
        ]

    def __str__(self):
        return self.name


class HallEquipment(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE,
                             related_name="hall_equipment", verbose_name="зал")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE,
                                  related_name="hall_links", verbose_name="оборудование")
    quantity = models.PositiveSmallIntegerField("количество",
                                                validators=[MinValueValidator(1), MaxValueValidator(20)])
    note = models.CharField("примечание", max_length=200, blank=True)

    class Meta:
        verbose_name = "оборудование зала"
        verbose_name_plural = "оборудование залов"
        ordering = ("hall", "equipment")
        constraints = [
            models.UniqueConstraint(fields=("hall", "equipment"), name="app_hallequipment_unique"),
            db_check(models.Q(quantity__gte=1, quantity__lte=20), "app_hallequipment_quantity_range"),
        ]

    def __str__(self):
        return f"{self.hall.name}: {self.equipment.name} x{self.quantity}"


class Slot(models.Model):
    class SlotStatus(models.TextChoices):
        OPEN = "open", "свободно"
        BOOKED = "booked", "занято"

    hall = models.ForeignKey(Hall, on_delete=models.CASCADE,
                             related_name="slots", verbose_name="зал")
    date = models.DateField("дата")
    start_time = models.TimeField("начало")
    end_time = models.TimeField("конец")
    status = models.CharField("статус окна", max_length=10,
                              choices=SlotStatus.choices, default=SlotStatus.OPEN)

    class Meta:
        verbose_name = "слот аренды"
        verbose_name_plural = "слоты аренды"
        ordering = ("date", "start_time")
        constraints = [
            models.UniqueConstraint(fields=("hall", "date", "start_time"),
                                    name="app_slot_unique_window"),
            db_check(models.Q(start_time__lt=models.F("end_time")), "app_slot_time_order"),
        ]

    def __str__(self):
        return f"{self.hall.name}, {self.date:%d.%m.%Y} {self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "запланировано"
        COMPLETED = "completed", "проведено"
        CANCELLED = "cancelled", "отменено"

    client = models.ForeignKey(Client, on_delete=models.PROTECT,
                               related_name="bookings", verbose_name="клиент")
    slot = models.OneToOneField(Slot, on_delete=models.PROTECT,
                                related_name="booking", verbose_name="слот")
    status = models.CharField("статус", max_length=10,
                              choices=Status.choices, default=Status.PLANNED)
    total_price = models.DecimalField("итоговая стоимость, руб.", max_digits=9, decimal_places=2)
    comment = models.CharField("комментарий", max_length=300, blank=True)
    created_at = models.DateTimeField("создана", auto_now_add=True)

    class Meta:
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"
        ordering = ("-created_at",)
        constraints = [
            db_check(models.Q(total_price__gte=0), "app_booking_total_positive"),
        ]

    def __str__(self):
        return f"Бронь #{self.pk} — {self.client.full_name}"


class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = "card", "карта"
        CASH = "cash", "наличные"
        TRANSFER = "transfer", "перевод"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                   related_name="payment", verbose_name="бронирование")
    amount = models.DecimalField("сумма, руб.", max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField("способ оплаты", max_length=10, choices=Method.choices)
    paid_at = models.DateTimeField("оплачено")

    class Meta:
        verbose_name = "оплата"
        verbose_name_plural = "оплаты"
        ordering = ("-paid_at",)
        constraints = [
            db_check(models.Q(amount__gte=0), "app_payment_amount_positive"),
        ]

    def __str__(self):
        return f"Оплата брони #{self.booking_id} — {self.amount} руб."


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                   related_name="review", verbose_name="бронирование")
    rating = models.PositiveSmallIntegerField("оценка",
                                              validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField("текст отзыва", blank=True)
    created_at = models.DateTimeField("создан", auto_now_add=True)

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = ("-created_at",)
        constraints = [
            db_check(models.Q(rating__gte=1, rating__lte=5), "app_review_rating_range"),
        ]

    def __str__(self):
        return f"Отзыв на бронь #{self.booking_id}: {self.rating}/5"
