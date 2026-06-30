from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.home,             name='home'),
    path('book/',                               views.booking_calendar, name='booking_calendar'),
    path('book/<int:slot_id>/',                 views.book_appointment, name='book_appointment'),
    path('book/success/<int:appointment_id>/',  views.booking_success,  name='booking_success'),
    path('my-appointments/',                    views.my_appointments,  name='my_appointments'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('dashboard/',                          views.dashboard,        name='dashboard'),
    path('dashboard/update/<int:appointment_id>/', views.update_status, name='update_status'),
    path('slots/',                              views.manage_slots,          name='manage_slots'),
    path('slots/reorder/',                      views.reorder_weekly_slots,  name='reorder_weekly_slots'),
    path('settings/',                           views.settings_view,    name='settings'),
]
