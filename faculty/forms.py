# forms.py
from django import forms
from controll.models import FacultyLeaveApplication
from django.core.exceptions import ValidationError
from datetime import date

class FacultyLeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = FacultyLeaveApplication
        fields = ['reason', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(FacultyLeaveApplicationForm, self).__init__(*args, **kwargs)
        # Customize form field widgets or labels as needed
        self.fields['reason'].widget.attrs.update({'placeholder': 'Enter the reason for leave'})
        self.fields['date_from'].widget.attrs.update({'placeholder': 'Select start date'})
        self.fields['date_to'].widget.attrs.update({'placeholder': 'Select end date'})

    def clean_date_from(self):
        date_from = self.cleaned_data['date_from']
        if date_from < date.today():
            raise ValidationError("The start date cannot be in the past. Please select a future date.")
        return date_from

    def clean_date_to(self):
        date_to = self.cleaned_data['date_to']
        date_from = self.cleaned_data.get('date_from')
        if date_to < date.today():
            raise ValidationError("The end date cannot be in the past. Please select a future date.")
        if date_from and date_to < date_from:
            raise ValidationError("The end date cannot be earlier than the start date.")
        return date_to
