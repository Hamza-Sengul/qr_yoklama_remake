from django import forms
from .models import Course, CourseStudent
from django.contrib.auth.models import User

class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'total_weeks', 'absence_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'total_weeks': forms.NumberInput(attrs={'class': 'form-control'}),
            'absence_limit': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AddStudentForm(forms.Form):
    student_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, academic_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(academic_user=academic_user)
