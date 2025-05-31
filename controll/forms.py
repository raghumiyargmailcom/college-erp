from django import forms
from .models import HOD, Principal
from .models import Subject

# ---------------- HOD FORM ----------------
class HODForm(forms.ModelForm):
    """Form for adding or updating HODs manually."""
    class Meta:
        model = HOD
        fields = ['hod_id', 'name', 'email', 'department', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

# ---------------- PRINCIPAL FORM ----------------
class PrincipalForm(forms.ModelForm):
    """Form for adding or updating Principals manually."""
    class Meta:
        model = Principal
        fields = ['name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }


        

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'department', 'semester']
        widgets = {
            'department': forms.Select(choices=Subject.DEPARTMENT_CHOICES, attrs={'class': 'form-control'}),
            'semester': forms.Select(choices=Subject.SEMESTER_CHOICES, attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

