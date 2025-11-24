# consumers/forms.py

from django import forms
from .models import Consumer, Barangay

class ConsumerForm(forms.ModelForm):
    # Date pickers for birth_date and registration_date
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    registration_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sort barangay dropdown alphabetically
        self.fields['barangay'].queryset = Barangay.objects.order_by('name')

    class Meta:
        model = Consumer
        # ✅ EXPLICIT FIELD LIST (sa halip na '__all__')
        fields = [
            # Personal Information
            'first_name', 'middle_name', 'last_name', 'birth_date', 'gender', 'phone_number',
            # Household Information
            'civil_status', 'spouse_name', 'barangay', 'purok', 'household_number',
            # Water Meter Information
            'usage_type', 'meter_brand', 'serial_number', 'first_reading', 'registration_date',
        ]
        widgets = {
            # Personal Information
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),

            # Household Information
            'civil_status': forms.Select(attrs={'class': 'form-select'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'barangay': forms.Select(attrs={'class': 'form-select'}),
            'purok': forms.Select(attrs={'class': 'form-select', 'id': 'id_purok'}),
            'household_number': forms.TextInput(attrs={'class': 'form-control'}),

            # Water Meter Information
            'usage_type': forms.Select(attrs={'class': 'form-select'}),
            'meter_brand': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_reading': forms.NumberInput(attrs={'class': 'form-control'}),
        }