# AppointEase — Client Appointment Scheduling Hub
### Complete project — Admin Dashboard + Customer Dashboard fully connected

---

## 🚀 Setup (run these 5 commands in order)

```bash
cd appointment_hub
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser        # set your admin username & password
python manage.py seed_data              # adds sample doctor profile + 30 open slots
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

---

## 🗺️ All Pages (fully connected)

### Public / Customer Side
| URL | Page | Purpose |
|---|---|---|
| `/` | Landing Page | Doctor profile, services, "Book Appointment" CTA |
| `/book/` | Slot Calendar | Pick an open date & time |
| `/book/<id>/` | Booking Form | Enter name/email/phone, double-booking blocked |
| `/book/success/<id>/` | Confirmation | Booking summary + link to My Appointments |
| `/my-appointments/` | **Customer Dashboard** | Look up bookings by email, cancel if needed |

### Provider / Admin Side (login required)
| URL | Page | Purpose |
|---|---|---|
| `/login/` | Provider Login | Staff login |
| `/dashboard/` | **Admin Dashboard** | Stat cards, appointment table, change status |
| `/slots/` | Manage Slots | Add/delete availability |
| `/settings/` | Profile Settings | Edit doctor info shown on landing page |
| `/admin/` | Django Admin | Full raw database access |

---

## 🔗 How Everything Connects

1. **Provider** logs in → adds slots in `/slots/` → updates profile in `/settings/`
2. **Client** visits `/` → sees profile + open slots → clicks "Book Appointment"
3. **Client** picks a slot in `/book/` → fills form → slot is instantly locked (`is_booked=True`)
4. **Client** gets confirmation page → can jump to `/my-appointments/` anytime using their email to view/cancel
5. **Provider** sees the new booking live on `/dashboard/` → changes status (Pending → Confirmed)
6. If a **client cancels**, the slot automatically reopens on the public calendar

---

## ✅ Tested Flows (verified working)
- Booking a slot → confirmation page ✔
- Double-booking prevention (slot locks immediately) ✔
- Customer dashboard email lookup ✔
- Customer self-service cancellation (slot reopens) ✔
- Admin login → dashboard redirect ✔
- Status update from dashboard table ✔
- Add/delete availability slots ✔
- Settings form updates landing page live ✔
- All pages mobile-responsive ✔

---

## 📁 Project Structure
```
appointment_hub/
├── appointment_hub/        settings.py, urls.py
├── booking/
│   ├── models.py           ProviderProfile, AvailabilitySlot, Appointment
│   ├── views.py            all 11 views (public + admin)
│   ├── forms.py            AppointmentForm, ProviderProfileForm
│   ├── urls.py             all routes
│   ├── admin.py            Django admin config
│   ├── management/commands/seed_data.py
│   └── templates/booking/
│       ├── base.html              navbar + footer + messages
│       ├── home.html              landing page
│       ├── calendar.html          slot picker
│       ├── appointment_form.html  booking form
│       ├── success.html           confirmation
│       ├── my_appointments.html   customer dashboard
│       ├── login.html             provider login
│       ├── dashboard.html         admin dashboard
│       ├── manage_slots.html      slot management
│       └── settings.html          profile editor
└── static/css/style.css    single stylesheet, fully responsive
```
