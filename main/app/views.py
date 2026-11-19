from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import Hall, Booking, Client, Slot
from .forms import BookingForm

def home(request):
    popular_halls = Hall.objects.filter(studio__is_active=True)[:3]
    return render(request, 'app/home.html', {'halls': popular_halls})

def catalog(request):
    query = request.GET.get('q', '')
    halls_list = Hall.objects.filter(studio__is_active=True)
    
    if query:
        halls_list = halls_list.filter(
            Q(name__icontains=query) | Q(studio__name__icontains=query) | Q(description__icontains=query)
        )
        
    paginator = Paginator(halls_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'app/catalog.html', {'page_obj': page_obj, 'query': query})

def api_search_halls(request):
    query = request.GET.get('q', '')
    halls = Hall.objects.filter(studio__is_active=True)
    
    if query:
        halls = halls.filter(
            Q(name__icontains=query) | Q(studio__name__icontains=query)
        )
    
    results = []
    for hall in halls[:5]:
        results.append({
            'id': hall.pk,
            'name': hall.name,
            'studio': hall.studio.name,
            'price': int(hall.hourly_rate),
            'url': f'/hall/{hall.pk}/'
        })
    
    return JsonResponse({'results': results, 'count': halls.count()})

def hall(request, pk):
    hall_obj = get_object_or_404(Hall, pk=pk)
    equipment = hall_obj.hall_equipment.all()
    return render(request, 'app/hall.html', {'hall': hall_obj, 'equipment': equipment})

def booking(request, pk):
    hall_obj = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            name = form.cleaned_data['name']
            client, created = Client.objects.get_or_create(phone=phone, defaults={'full_name': name})
            
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['time']
            end_time = (datetime.combine(date, start_time) + timedelta(hours=1)).time()
            
            slot, slot_created = Slot.objects.get_or_create(
                hall=hall_obj, date=date, start_time=start_time,
                defaults={'end_time': end_time, 'status': 'booked'}
            )
            
            if not slot_created and hasattr(slot, 'booking'):
                form.add_error(None, "Это время уже занято, выберите другое.")
            else:
                Booking.objects.create(client=client, slot=slot, total_price=hall_obj.hourly_rate, status='planned')
                slot.status = 'booked'
                slot.save()
                request.session['client_phone'] = phone
                messages.success(request, f'Заявка на зал «{hall_obj.name}» успешно отправлена!')
                return redirect('app:account')
    else:
        form = BookingForm()
    return render(request, 'app/booking.html', {'hall': hall_obj, 'form': form})

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if Client.objects.filter(phone=phone).exists():
            request.session['client_phone'] = phone
            messages.success(request, 'Вы успешно вошли в личный кабинет!')
            return redirect('app:account')
        else:
            messages.error(request, 'Клиент с таким номером телефона не найден. Пожалуйста, сначала оформите бронирование.')
    
    return render(request, 'app/login.html')

def logout_view(request):
    if 'client_phone' in request.session:
        del request.session['client_phone']
    messages.success(request, 'Вы вышли из личного кабинета.')
    return redirect('app:home')

def account(request):
    phone = request.session.get('client_phone')
    if not phone:
        messages.warning(request, 'Пожалуйста, войдите в кабинет, чтобы увидеть бронирования.')
        return redirect('app:login')
        
    bookings = Booking.objects.filter(client__phone=phone).select_related('slot__hall', 'client').order_by('-created_at')
    return render(request, 'app/account.html', {'bookings': bookings})

def cancel_booking(request, pk):
    booking_obj = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking_obj.slot.status = 'open'
        booking_obj.slot.save()
        booking_obj.delete()
        messages.success(request, 'Бронирование успешно отменено.')
    return redirect('app:account')

def about(request):
    return render(request, 'app/about.html')