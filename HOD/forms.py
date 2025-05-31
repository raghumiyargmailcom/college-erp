from django import forms
from controll.models import Timetable 


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['day', 'slot_1', 'slot_2', 'slot_3', 'slot_4', 'slot_5', 'slot_6', 'slot_7']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'slot_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:30 - 10:15'}),
            'slot_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10:20 - 11:05'}),
            'slot_3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11:15 - 12:00'}),
            'slot_4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12:00 - 12:45'}),
            'slot_5': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01:45 - 02:45'}),
            'slot_6': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '02:45 - 03:45'}),
            'slot_7': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03:55 - 04:55'}),
        }



    from django import forms
from controll.models import Marks, Childrens, Subject

class MarksEntryForm(forms.Form):
    rollno = forms.CharField(label="Student Roll Number", max_length=20)
    semester = forms.ChoiceField(label="Semester", choices=[
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
    ])
    max_marks = forms.IntegerField(label="Maximum Marks", min_value=1, required=True)

    def __init__(self, *args, **kwargs):
        subjects = kwargs.pop('subjects', None)  # Get subjects dynamically
        max_marks = kwargs.pop('max_marks', 100)  # Default max marks is 100
        super().__init__(*args, **kwargs)

        # Dynamically add subject fields based on semester
        if subjects:
            for subject in subjects:
                field_name = f"subject_{subject.id}"  # Unique field for each subject
                self.fields[field_name] = forms.IntegerField(
                    label=f"{subject.name} Marks (Max: {max_marks})",
                    min_value=0,
                    max_value=max_marks,
                    required=True
                )
