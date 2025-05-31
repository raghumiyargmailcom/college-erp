from django import forms
from controll.models import Childrens  # ✅ Import from 'controll' app

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating student profile photo, phone number, and address."""
    class Meta:
        model = Childrens
        fields = ['profile_photo', 'phone_number', 'address']  # ✅ Only these fields are editable

        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
        }
