from django.db import models

class ProviderProfile(models.Model):
    name = models.CharField(max_length=100, default="Dr. Priya Sharma")
    title = models.CharField(max_length=150, default="General Physician")
    specialization = models.CharField(max_length=150, default="General Medicine")
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    years_experience = models.PositiveIntegerField(default=5)
    consultation_fee = models.PositiveIntegerField(default=500)
    languages = models.CharField(max_length=200, default="English, Hindi")

    def __str__(self):
        return self.name

SLOT_COLORS = [
    ('#3b82f6', 'Blue'),
    ('#10b981', 'Emerald'),
    ('#f59e0b', 'Amber'),
    ('#8b5cf6', 'Violet'),
    ('#ec4899', 'Pink'),
    ('#14b8a6', 'Teal'),
    ('#ef4444', 'Red'),
    ('#6366f1', 'Indigo'),
]

class WeeklySlotTemplate(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    day_of_week = models.IntegerField(choices=DAYS)
    name        = models.CharField(max_length=100)
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    is_active   = models.BooleanField(default=True)
    color       = models.CharField(max_length=20, default='#3b82f6')
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['day_of_week', 'sort_order', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} — {self.name}"


class SlotTemplate(models.Model):
    name       = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time   = models.TimeField()
    is_active  = models.BooleanField(default=True)
    color      = models.CharField(max_length=20, default='#3b82f6')

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%I:%M %p')} – {self.end_time.strftime('%I:%M %p')})"


class AvailabilitySlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.date} {self.start_time.strftime('%I:%M %p')} [{status}]"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name='appointment')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['slot__date', 'slot__start_time']

    def __str__(self):
        return f"{self.client_name} — {self.slot.date}"
