from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('search/', views.search, name='search'),
    path('hall/<int:pk>/', views.hall_detail, name='hall_detail'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('login/', views.login_view, name='login'),
    path('account/', views.account, name='account'),
    path('about/', views.about, name='about'),
]