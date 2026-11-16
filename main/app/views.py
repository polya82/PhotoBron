from django.shortcuts import render
from .models import Hall

def home(request):
    popular_halls = Hall.objects.filter(studio__is_active=True)[:3]
    return render(request, 'app/home.html', {'halls': popular_halls})

def catalog(request):
    return render(request, 'app/catalog.html')

def hall_detail(request, pk):
    return render(request, 'app/hall_detail.html')

def booking(request, pk):
    return render(request, 'app/booking.html')

def login_view(request):
    return render(request, 'app/login.html')

def account(request):
    return render(request, 'app/account.html')