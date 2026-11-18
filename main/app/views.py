from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Hall, Booking
from .forms import BookingForm

def home(request):
    popular_halls = Hall.objects.filter(studio__is_active=True)[:3]
    return render(request, 'app/home.html', {'halls': popular_halls})

def catalog(request):
    halls_list = Hall.objects.filter(studio__is_active=True)
    paginator = Paginator(halls_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/catalog.html', {'page_obj': page_obj})

def search(request):
    query = request.GET.get('q', '')
    halls_list = Hall.objects.filter(studio__is_active=True)
    if query:
        halls_list = halls_list.filter(
            Q(name__icontains=query) | Q(studio__name__icontains=query) | Q(description__icontains=query)
        )
    paginator = Paginator(halls_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/search.html', {'page_obj': page_obj, 'query': query})

def hall_detail(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    equipment = hall.hall_equipment.all()
    return render(request, 'app/hall_detail.html', {'hall': hall, 'equipment': equipment})

def booking(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            messages.success(request, f'Заявка на зал «{hall.name}» успешно отправлена!')
            return redirect('app:home')
    else:
        form = BookingForm()
    return render(request, 'app/booking.html', {'hall': hall, 'form': form})

def login_view(request):
    return render(request, 'app/login.html')

def account(request):
    bookings = Booking.objects.all().select_related('slot__hall', 'client')
    return render(request, 'app/account.html', {'bookings': bookings})

def about(request):
    return render(request, 'app/about.html')