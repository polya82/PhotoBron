from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('api/search/', views.api_search_halls, name='api_search'),
    path('hall/<int:pk>/', views.hall, name='hall'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('account/', views.account, name='account'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    path('about/', views.about, name='about'),
]