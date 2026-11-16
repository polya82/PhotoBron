from django.db.models import Avg, Count, Q

from app.models import Booking, Hall

LINE = "=" * 70


def show(num, title, orm_code, qs, columns, rows):
    print(LINE)
    print(f"Запрос {num}. {title}")
    print(LINE)
    print("ORM:", orm_code)
    print("SQL:", qs.query)
    print(f"Результат ({len(rows)} строк):")
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(x) for x in row))
    print()


qs1 = (Booking.objects.filter(status=Booking.Status.PLANNED, total_price__gte=5000)
       .select_related("client", "slot__hall").order_by("-total_price"))
rows1 = [(b.pk, b.client.full_name, b.slot.hall.name, b.total_price) for b in qs1]
show(1, "запланированные брони дороже 5000 руб.",
     'Booking.objects.filter(status=Booking.Status.PLANNED, total_price__gte=5000).select_related("client", "slot__hall").order_by("-total_price")',
     qs1, ["id брони", "клиент", "зал", "сумма"], rows1)

qs2 = (Hall.objects.annotate(avg_rating=Avg("slots__booking__review__rating"),
                             reviews=Count("slots__booking__review"))
       .order_by("-avg_rating")[:5])
rows2 = [(h.name, h.avg_rating, h.reviews) for h in qs2]
show(2, "топ-5 залов по средней оценке",
     'Hall.objects.annotate(avg_rating=Avg("slots__booking__review__rating"), reviews=Count("slots__booking__review")).order_by("-avg_rating")[:5]',
     qs2, ["зал", "средняя оценка", "отзывов"], rows2)

active = ~Q(slots__booking__status="cancelled")
qs3 = (Hall.objects.annotate(cnt=Count("slots__booking", filter=active),
                             avg_price=Avg("slots__booking__total_price", filter=active))
       .order_by("name"))
rows3 = [(h.name, h.cnt, h.avg_price if h.avg_price is not None else "—") for h in qs3]
show(3, "число активных броней и средний чек по залам",
     'Hall.objects.annotate(cnt=Count("slots__booking", filter=~Q(slots__booking__status="cancelled")), avg_price=Avg("slots__booking__total_price", filter=~Q(slots__booking__status="cancelled"))).order_by("name")',
     qs3, ["зал", "броней", "средний чек"], rows3)

qs4 = (Booking.objects.filter(status=Booking.Status.COMPLETED)
       .select_related("client", "slot__hall__studio", "payment").order_by("-slot__date")[:10])
rows4 = [(b.pk, b.client.full_name, b.slot.hall.studio.name, b.slot.hall.name,
          b.slot.date, b.total_price, b.payment.method if hasattr(b, "payment") else "—")
         for b in qs4]
show(4, "проведённые брони одним запросом без N+1",
     'Booking.objects.filter(status=Booking.Status.COMPLETED).select_related("client", "slot__hall__studio", "payment").order_by("-slot__date")[:10]',
     qs4, ["бронь", "клиент", "студия", "зал", "дата", "сумма", "оплата"], rows4)

qs5 = Hall.objects.prefetch_related("hall_equipment__equipment").order_by("name")
rows5 = []
for h in qs5:
    items = [f"{he.equipment.name} x{he.quantity}" for he in h.hall_equipment.all()]
    rows5.append((h.name, "; ".join(items)))
show(5, "оборудование каждого зала (2 запроса вместо N)",
     'Hall.objects.prefetch_related("hall_equipment__equipment").order_by("name")',
     qs5, ["зал", "оборудование"], rows5)
