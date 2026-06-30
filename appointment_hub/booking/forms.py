from django import forms
from .models import Appointment, ProviderProfile

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client_name', 'client_email', 'client_phone', 'message']
        widgets = {
            'client_name':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your full name'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'message':      forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Reason for appointment (optional)', 'rows': 3}),
        }
        labels = {
            'client_name': 'Full Name', 'client_email': 'Email Address',
            'client_phone': 'Phone Number', 'message': 'Message (Optional)',
        }

    def clean_client_phone(self):
        phone = self.cleaned_data.get('client_phone', '').strip()
        if len(''.join(filter(str.isdigit, phone))) < 7:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = ['name', 'title', 'specialization', 'bio', 'phone', 'email', 'location', 'years_experience', 'consultation_fee', 'languages']
        widgets = {
            'name':             forms.TextInput(attrs={'class': 'form-input'}),
            'title':            forms.TextInput(attrs={'class': 'form-input'}),
            'specialization':   forms.TextInput(attrs={'class': 'form-input'}),
            'bio':              forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'phone':            forms.TextInput(attrs={'class': 'form-input'}),
            'email':            forms.EmailInput(attrs={'class': 'form-input'}),
            'location':         forms.TextInput(attrs={'class': 'form-input'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-input'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-input'}),
            'languages':        forms.TextInput(attrs={'class': 'form-input'}),
        }
