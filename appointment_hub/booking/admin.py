from django.contrib import admin
from .models import ProviderProfile, AvailabilitySlot, Appointment, SlotTemplate, WeeklySlotTemplate

@admin.register(SlotTemplate)
class SlotTemplateAdmin(admin.ModelAdmin):
    list_display  = ['name', 'start_time', 'end_time', 'is_active']
    list_filter   = ['is_active']
    list_editable = ['is_active']

@admin.register(WeeklySlotTemplate)
class WeeklySlotTemplateAdmin(admin.ModelAdmin):
    list_display  = ['get_day_of_week_display', 'name', 'start_time', 'end_time', 'is_active']
    list_filter   = ['day_of_week', 'is_active']
    list_editable = ['is_active']
    ordering      = ['day_of_week', 'start_time']

@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email', 'phone']

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display  = ['date', 'start_time', 'end_time', 'is_booked']
    list_filter   = ['date', 'is_booked']
    list_editable = ['is_booked']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['client_name', 'client_email', 'slot', 'status', 'created_at']
    list_filter   = ['status']
    list_editable = ['status']
    search_fields = ['client_name', 'client_email']
