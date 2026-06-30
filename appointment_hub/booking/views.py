from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from collections import defaultdict
from .models import AvailabilitySlot, Appointment, ProviderProfile, SlotTemplate, WeeklySlotTemplate, SLOT_COLORS
from .forms import AppointmentForm, ProviderProfileForm
import datetime, json

def home(request):
    profile = ProviderProfile.objects.first()
    available_count = AvailabilitySlot.objects.filter(is_booked=False, date__gte=timezone.now().date()).count()
    return render(request, 'booking/home.html', {'profile': profile, 'available_count': available_count})

def booking_calendar(request):
    today = timezone.now().date()
    slots = AvailabilitySlot.objects.filter(date__gte=today, is_booked=False)
    grouped = defaultdict(list)
    for slot in slots:
        grouped[slot.date].append(slot)
    return render(request, 'booking/calendar.html', {'grouped_slots': dict(grouped)})

def book_appointment(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)
    if slot.is_booked:
        messages.error(request, "This slot was just booked. Please choose another.")
        return redirect('booking_calendar')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            slot.refresh_from_db()
            if slot.is_booked:
                messages.error(request, "This slot was just taken. Please choose another.")
                return redirect('booking_calendar')
            appointment = form.save(commit=False)
            appointment.slot = slot
            appointment.save()
            slot.is_booked = True
            slot.save()
            return redirect('booking_success', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'booking/appointment_form.html', {'form': form, 'slot': slot})

def booking_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'booking/success.html', {'appointment': appointment})

def my_appointments(request):
    appointments = None
    searched_email = request.GET.get('email', '').strip().lower() or None
    if request.method == 'POST':
        searched_email = request.POST.get('email', '').strip().lower()
    if searched_email:
        appointments = Appointment.objects.select_related('slot').filter(
            client_email__iexact=searched_email
        ).order_by('-slot__date')
        if not appointments.exists():
            messages.error(request, "No appointments found for this email.")
    return render(request, 'booking/my_appointments.html', {
        'appointments': appointments,
        'searched_email': searched_email,
        'today': timezone.now().date(),
    })

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        if appointment.status != 'cancelled':
            appointment.status = 'cancelled'
            appointment.save()
            appointment.slot.is_booked = False
            appointment.slot.save()
            messages.success(request, "Your appointment has been cancelled.")
        return redirect(f"/my-appointments/?email={appointment.client_email}")
    return redirect('my_appointments')


@login_required
def dashboard(request):
    today = timezone.now().date()
    all_appts = Appointment.objects.select_related('slot').all()
    upcoming  = all_appts.filter(slot__date__gte=today)
    past      = all_appts.filter(slot__date__lt=today)
    stats = {
        'total':     all_appts.count(),
        'pending':   all_appts.filter(status='pending').count(),
        'confirmed': all_appts.filter(status='confirmed').count(),
        'cancelled': all_appts.filter(status='cancelled').count(),
        'today':     all_appts.filter(slot__date=today).count(),
    }
    return render(request, 'booking/dashboard.html', {
        'upcoming': upcoming, 'past': past, 'stats': stats, 'today': today,
    })

@login_required
def update_status(request, appointment_id):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appointment_id)
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'cancelled']:
            appt.status = new_status
            appt.save()
            messages.success(request, f"Appointment for {appt.client_name} marked as {new_status}.")
    return redirect('dashboard')

@login_required
def reorder_weekly_slots(request):
    if request.method == 'POST':
        try:
            ids = json.loads(request.POST.get('order', '[]'))
            for i, sid in enumerate(ids):
                WeeklySlotTemplate.objects.filter(id=int(sid)).update(sort_order=i)
            return JsonResponse({'ok': True})
        except Exception:
            return JsonResponse({'ok': False}, status=400)
    return JsonResponse({'ok': False}, status=405)


@login_required
def manage_slots(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_template':
            name       = request.POST.get('name', '').strip()
            start_time = request.POST.get('start_time')
            end_time   = request.POST.get('end_time')
            color      = request.POST.get('color', '#3b82f6')
            if name and start_time and end_time:
                SlotTemplate.objects.create(name=name, start_time=start_time, end_time=end_time, color=color)
                messages.success(request, f"Template '{name}' added.")
            else:
                messages.error(request, "Please fill all template fields.")

        elif action == 'edit_template':
            tmpl = get_object_or_404(SlotTemplate, id=request.POST.get('template_id'))
            name       = request.POST.get('name', '').strip()
            start_time = request.POST.get('start_time')
            end_time   = request.POST.get('end_time')
            is_active  = request.POST.get('is_active') == 'on'
            color      = request.POST.get('color', tmpl.color)
            if name and start_time and end_time:
                tmpl.name, tmpl.start_time, tmpl.end_time, tmpl.is_active, tmpl.color = name, start_time, end_time, is_active, color
                tmpl.save()
                messages.success(request, f"Template '{name}' updated.")
            else:
                messages.error(request, "Please fill all fields.")

        elif action == 'delete_template':
            tmpl = get_object_or_404(SlotTemplate, id=request.POST.get('template_id'))
            tmpl.delete()
            messages.success(request, "Template deleted.")

        elif action == 'schedule':
            date         = request.POST.get('date')
            template_ids = request.POST.getlist('template_ids')
            if date and template_ids:
                slot_date = datetime.date.fromisoformat(date)
                if slot_date < timezone.now().date():
                    messages.error(request, "Cannot schedule slots for past dates.")
                else:
                    created = skipped = 0
                    for tmpl_id in template_ids:
                        tmpl = get_object_or_404(SlotTemplate, id=tmpl_id)
                        exists = AvailabilitySlot.objects.filter(
                            date=slot_date, start_time=tmpl.start_time, end_time=tmpl.end_time
                        ).exists()
                        if not exists:
                            AvailabilitySlot.objects.create(
                                date=slot_date,
                                start_time=tmpl.start_time,
                                end_time=tmpl.end_time,
                            )
                            created += 1
                        else:
                            skipped += 1
                    msg = f"{created} slot(s) scheduled for {date}."
                    if skipped:
                        msg += f" {skipped} duplicate(s) skipped."
                    messages.success(request, msg)
            else:
                messages.error(request, "Select a date and at least one template.")

        elif action == 'delete':
            slot = get_object_or_404(AvailabilitySlot, id=request.POST.get('slot_id'))
            if slot.is_booked:
                messages.error(request, "Cannot delete a booked slot.")
            else:
                slot.delete()
                messages.success(request, "Slot deleted.")

        elif action == 'add_weekly':
            day  = request.POST.get('day_of_week')
            name = request.POST.get('name', '').strip()
            start_time = request.POST.get('start_time')
            end_time   = request.POST.get('end_time')
            color      = request.POST.get('color', '#3b82f6')
            if day is not None and name and start_time and end_time:
                max_order = WeeklySlotTemplate.objects.filter(day_of_week=int(day)).count()
                WeeklySlotTemplate.objects.create(
                    day_of_week=int(day), name=name,
                    start_time=start_time, end_time=end_time,
                    color=color, sort_order=max_order,
                )
                messages.success(request, f"Weekly slot added for {WeeklySlotTemplate.DAYS[int(day)][1]}.")
            else:
                messages.error(request, "Please fill all fields.")

        elif action == 'edit_weekly':
            ws = get_object_or_404(WeeklySlotTemplate, id=request.POST.get('weekly_id'))
            name       = request.POST.get('name', '').strip()
            start_time = request.POST.get('start_time')
            end_time   = request.POST.get('end_time')
            is_active  = request.POST.get('is_active') == 'on'
            color      = request.POST.get('color', ws.color)
            if name and start_time and end_time:
                ws.name, ws.start_time, ws.end_time, ws.is_active, ws.color = name, start_time, end_time, is_active, color
                ws.save()
                messages.success(request, f"Weekly slot '{name}' updated.")
            else:
                messages.error(request, "Please fill all fields.")

        elif action == 'delete_weekly':
            ws = get_object_or_404(WeeklySlotTemplate, id=request.POST.get('weekly_id'))
            ws.delete()
            messages.success(request, "Weekly slot deleted.")

        elif action == 'apply_weekly':
            date = request.POST.get('date')
            day  = request.POST.get('day_of_week')
            if date and day is not None:
                slot_date = datetime.date.fromisoformat(date)
                if slot_date < timezone.now().date():
                    messages.error(request, "Cannot schedule slots for past dates.")
                else:
                    weekly = WeeklySlotTemplate.objects.filter(day_of_week=int(day), is_active=True)
                    created = skipped = 0
                    for ws in weekly:
                        exists = AvailabilitySlot.objects.filter(
                            date=slot_date, start_time=ws.start_time, end_time=ws.end_time
                        ).exists()
                        if not exists:
                            AvailabilitySlot.objects.create(
                                date=slot_date, start_time=ws.start_time, end_time=ws.end_time
                            )
                            created += 1
                        else:
                            skipped += 1
                    msg = f"{created} slot(s) applied to {date}."
                    if skipped:
                        msg += f" {skipped} duplicate(s) skipped."
                    messages.success(request, msg)
            else:
                messages.error(request, "Invalid request.")

        elif action == 'schedule_week':
            week_start_str = request.POST.get('week_start')
            if week_start_str:
                week_start = datetime.date.fromisoformat(week_start_str)
                today_d    = timezone.now().date()
                created = skipped = 0
                for day_num, day_name in WeeklySlotTemplate.DAYS:
                    target = week_start + datetime.timedelta(days=day_num)
                    if target < today_d:
                        continue
                    for ws in WeeklySlotTemplate.objects.filter(day_of_week=day_num, is_active=True):
                        exists = AvailabilitySlot.objects.filter(
                            date=target, start_time=ws.start_time, end_time=ws.end_time
                        ).exists()
                        if not exists:
                            AvailabilitySlot.objects.create(date=target, start_time=ws.start_time, end_time=ws.end_time)
                            created += 1
                        else:
                            skipped += 1
                messages.success(request, f"{created} slot(s) scheduled for the week. {skipped} duplicate(s) skipped.")
            else:
                messages.error(request, "Please select a week start date.")

        elif action == 'copy_next_week':
            today_d        = timezone.now().date()
            current_monday = today_d - datetime.timedelta(days=today_d.weekday())
            week_end       = current_monday + datetime.timedelta(days=6)
            this_week      = AvailabilitySlot.objects.filter(date__gte=current_monday, date__lte=week_end)
            created = skipped = 0
            for slot in this_week:
                new_date = slot.date + datetime.timedelta(weeks=1)
                if not AvailabilitySlot.objects.filter(date=new_date, start_time=slot.start_time, end_time=slot.end_time).exists():
                    AvailabilitySlot.objects.create(date=new_date, start_time=slot.start_time, end_time=slot.end_time)
                    created += 1
                else:
                    skipped += 1
            messages.success(request, f"Copied {created} slot(s) to next week. {skipped} duplicate(s) skipped.")

        return redirect('manage_slots')

    today     = timezone.now().date()
    today_dow = today.weekday()
    templates = SlotTemplate.objects.all()
    edit_id   = request.GET.get('edit')
    edit_tmpl = SlotTemplate.objects.filter(id=edit_id).first() if edit_id else None
    edit_wid  = request.GET.get('edit_w')

    # Weekly slots grouped by day
    by_day = defaultdict(list)
    for ws in WeeklySlotTemplate.objects.all():
        by_day[ws.day_of_week].append(ws)
    days_with_slots = [
        (day_num, day_name, by_day.get(day_num, []))
        for day_num, day_name in WeeklySlotTemplate.DAYS
    ]

    # Scheduled slots grouped by date
    slots   = AvailabilitySlot.objects.all()
    grouped = defaultdict(list)
    for s in slots:
        grouped[s.date].append(s)

    # Heatmap: 8 weeks starting 2 weeks ago (Monday)
    hm_start = today - datetime.timedelta(days=today.weekday() + 14)
    heatmap_weeks = []
    for w in range(8):
        week = []
        for d in range(7):
            dt      = hm_start + datetime.timedelta(weeks=w, days=d)
            slist   = grouped.get(dt, [])
            total   = len(slist)
            booked  = sum(1 for s in slist if s.is_booked)
            week.append({
                'date':     dt,
                'total':    total,
                'booked':   booked,
                'pct':      int(booked / total * 100) if total else 0,
                'is_today': dt == today,
                'is_past':  dt < today,
            })
        heatmap_weeks.append(week)

    # Next Monday for "Schedule Full Week"
    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + datetime.timedelta(days=days_until_monday)

    return render(request, 'booking/manage_slots.html', {
        'templates':       templates,
        'edit_tmpl':       edit_tmpl,
        'edit_wid':        edit_wid,
        'days_with_slots': days_with_slots,
        'today_dow':       today_dow,
        'grouped_slots':   dict(grouped),
        'today':           today,
        'heatmap_weeks':   heatmap_weeks,
        'next_monday':     next_monday,
        'slot_colors':     SLOT_COLORS,
    })

@login_required
def settings_view(request):
    profile, _ = ProviderProfile.objects.get_or_create(id=1, defaults={'name': 'Dr. Provider'})
    if request.method == 'POST':
        form = ProviderProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('settings')
    else:
        form = ProviderProfileForm(instance=profile)
    return render(request, 'booking/settings.html', {'form': form, 'profile': profile})
