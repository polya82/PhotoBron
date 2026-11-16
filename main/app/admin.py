from django.contrib import admin

from .models import (Studio, Hall, Client, Equipment, HallEquipment,
                     Slot, Booking, Payment, Review)


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "contact_phone", "is_active")
    search_fields = ("name", "address")


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "studio", "capacity", "hourly_rate")
    list_filter = ("studio",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "created_at")
    search_fields = ("full_name", "phone")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "hourly_price")
    list_filter = ("category",)


@admin.register(HallEquipment)
class HallEquipmentAdmin(admin.ModelAdmin):
    list_display = ("hall", "equipment", "quantity", "note")


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("hall", "date", "start_time", "end_time", "status")
    list_filter = ("hall", "status")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "slot", "status", "total_price", "created_at")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "method", "paid_at")
    list_filter = ("method",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "created_at")
    list_filter = ("rating",)
