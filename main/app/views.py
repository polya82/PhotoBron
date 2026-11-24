from datetime import datetime

import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import OperationalError, IntegrityError, transaction
from django.contrib import messages
from django.http import JsonResponse

from .models import Hall, Booking, Client, Slot
from .forms import BookingForm

logger = logging.getLogger('app')


def normalize_phone(raw):
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if len(digits) == 11 and digits[0] == '8':
        digits = '7' + digits[1:]
    if len(digits) == 10:
        digits = '7' + digits
    return '+' + digits


def home(request):
    try:
        popular_halls = Hall.objects.filter(studio__is_active=True)[:3]
    except OperationalError:
        logger.error('База данных недоступна при открытии главной страницы', exc_info=True)
        return render(request, '500.html', status=500)
    logger.debug('Главная страница: выбрано популярных залов %s', len(popular_halls))
    return render(request, 'app/home.html', {'halls': popular_halls})


def catalog(request):
    query = request.GET.get('q', '')
    logger.debug('Каталог открыт, параметр поиска: %r', query)

    try:
        halls_list = Hall.objects.filter(studio__is_active=True)

        if query:
            halls_list = halls_list.filter(
                Q(name__icontains=query) | Q(studio__name__icontains=query) | Q(description__icontains=query)
            )

        paginator = Paginator(halls_list, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
    except OperationalError:
        logger.error('База данных недоступна при открытии каталога', exc_info=True)
        return render(request, '500.html', status=500)

    return render(request, 'app/catalog.html', {'page_obj': page_obj, 'query': query})


def api_search_halls(request):
    query = request.GET.get('q', '')
    results = []

    try:
        halls = Hall.objects.filter(studio__is_active=True)

        if query:
            halls = halls.filter(
                Q(name__icontains=query) | Q(studio__name__icontains=query)
            )

        for hall in halls[:5]:
            results.append({
                'id': hall.pk,
                'name': hall.name,
                'studio': hall.studio.name,
                'price': int(hall.hourly_rate),
                'url': f'/hall/{hall.pk}/'
            })

        count = halls.count()
    except OperationalError:
        logger.error('Ошибка БД при живом поиске: q=%r', query, exc_info=True)
        count = 0

    logger.debug('Живой поиск: q=%r, найдено залов %s', query, len(results))
    return JsonResponse({'results': results, 'count': count})


def hall(request, pk):
    hall_obj = get_object_or_404(Hall, pk=pk)
    equipment = hall_obj.hall_equipment.all()
    return render(request, 'app/hall.html', {'hall': hall_obj, 'equipment': equipment})


def booking(request, pk):
    hall_obj = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            phone = normalize_phone(form.cleaned_data['phone'])
            name = form.cleaned_data['name']
            logger.info('Получена заявка на бронирование зала id=%s, телефон %s', hall_obj.pk, phone)
            client, created = Client.objects.get_or_create(phone=phone, defaults={'full_name': name})

            date = form.cleaned_data['date']
            start_time = form.cleaned_data['time']
            end_time = form.cleaned_data['time_end']

            if end_time <= start_time:
                form.add_error("time_end", "Время окончания должно быть позже времени начала.")
                logger.warning('Заявка на зал id=%s отклонена: конец раньше начала', hall_obj.pk)
                return render(request, "app/booking.html", {"hall": hall_obj, "form": form})

            if end_time.hour >= 23:
                form.add_error("time_end", "Бронирование возможно не позднее 22:00")
                logger.warning('Заявка на зал id=%s отклонена: время позже 22:00', hall_obj.pk)
                return render(request, "app/booking.html", {"hall": hall_obj, "form": form})

            if datetime.combine(date, start_time) < datetime.now():
                form.add_error(None, "Нельзя забронировать зал на прошедшее время. Выберите другую дату или время.")
                logger.warning('Заявка на зал id=%s отклонена: прошедшее время', hall_obj.pk)
                return render(request, "app/booking.html", {"hall": hall_obj, "form": form})

            overlap = Slot.objects.filter(
                hall=hall_obj, date=date, status='booked',
                start_time__lt=end_time, end_time__gt=start_time
            ).exists()
            if overlap:
                form.add_error(None, "Это время уже занято. Выберите другой интервал.")
                logger.warning('Заявка на зал id=%s отклонена: слот занят', hall_obj.pk)
                return render(request, "app/booking.html", {"hall": hall_obj, "form": form})

            hours = int((datetime.combine(date, end_time) - datetime.combine(date, start_time)).total_seconds() // 3600)

            # защита от дубликата брони: слот и бронь создаются атомарно,
            # при ошибке в середине операции данные не меняются
            try:
                with transaction.atomic():
                    slot = Slot.objects.create(
                        hall=hall_obj, date=date,
                        start_time=start_time, end_time=end_time, status='booked'
                    )
                    Booking.objects.create(client=client, slot=slot,
                                           total_price=hall_obj.hourly_rate * hours, status='planned')
            except IntegrityError:
                logger.warning('Дубликат брони: зал id=%s, %s %s', hall_obj.pk, date, start_time)
                messages.error(request, 'Это время уже занято, выберите другое.')
                return redirect('app:catalog')

            request.session['client_phone'] = phone
            logger.info('Бронирование создано: зал id=%s, слот id=%s, клиент %s, часов %s',
                        hall_obj.pk, slot.pk, phone, hours)
            messages.success(request, f'Заявка на зал «{hall_obj.name}» успешно отправлена!')
            return redirect('app:account')

        logger.warning('Форма брони не прошла валидацию: %s', form.errors)
    else:
        form = BookingForm()
    return render(request, 'app/booking.html', {'hall': hall_obj, 'form': form})


def login_view(request):
    if request.session.get('client_phone'):
        return redirect('app:account')

    now_ts = datetime.now().timestamp()
    blocked_until = request.session.get('blocked_until')
    if blocked_until and now_ts < blocked_until:
        messages.error(request, 'Слишком много попыток входа. Попробуйте через 10 минут.')
        return redirect('app:login')

    if request.method == 'POST':
        phone = normalize_phone(request.POST.get('phone', ''))
        client = Client.objects.filter(phone=phone).first()
        if client:
            request.session.pop('login_attempts', None)
            request.session['client_phone'] = client.phone
            return redirect('app:account')

        attempts = request.session.get('login_attempts', 0) + 1
        if attempts >= 5:
            request.session['blocked_until'] = now_ts + 600
            request.session.pop('login_attempts', None)
            logger.warning('Вход заблокирован на 10 минут: телефон %r', phone)
            messages.error(request, 'Слишком много попыток входа. Попробуйте через 10 минут.')
        else:
            request.session['login_attempts'] = attempts
            messages.error(request, 'Клиент с таким номером телефона не найден. Пожалуйста, сначала оформите бронирование.')
        return redirect('app:login')

    return render(request, 'app/login.html')


def logout_view(request):
    if 'client_phone' in request.session:
        del request.session['client_phone']
    messages.success(request, 'Вы вышли из личного кабинета.')
    return redirect('app:home')


def account(request):
    phone = request.session.get('client_phone')
    if not phone:
        # гость в кабинете / истёкшая сессия — не падаем, отправляем на вход
        logger.info('Попытка доступа в кабинет без сессии')
        messages.warning(request, 'Пожалуйста, войдите в кабинет, чтобы увидеть бронирования.')
        return redirect('app:login')

    bookings = Booking.objects.filter(client__phone=phone).select_related('slot__hall', 'client').order_by('-created_at')
    logger.debug('Личный кабинет: телефон %s, бронирований %s', phone, len(bookings))
    return render(request, 'app/account.html', {'bookings': bookings})


def cancel_booking(request, pk):
    client_phone = request.session.get('client_phone')
    if not client_phone:
        messages.error(request, 'Сначала войдите по номеру телефона.')
        return redirect('app:login')

    booking_obj = get_object_or_404(Booking, pk=pk)

    if booking_obj.client.phone != client_phone:
        # нет прав на действие — Django отдаст шаблон 403.html
        logger.warning('Попытка отменить чужую бронь id=%s с телефона %s', booking_obj.pk, client_phone)
        raise PermissionDenied

    if request.method == 'POST':
        try:
            with transaction.atomic():
                booking_obj.slot.status = 'open'
                booking_obj.slot.save()
                booking_obj.delete()
        except OperationalError:
            logger.error('БД недоступна при отмене брони id=%s', booking_obj.pk, exc_info=True)
            messages.error(request, 'Не удалось отменить бронирование, попробуйте позже.')
            return redirect('app:account')

        logger.info('Бронирование id=%s отменено клиентом %s', booking_obj.pk, client_phone)
        messages.success(request, 'Бронирование успешно отменено.')
    return redirect('app:account')


def about(request):
    return render(request, 'app/about.html')
