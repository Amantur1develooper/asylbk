from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Иванов Иван Иванович'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 700 000 000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'passport_copy': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'personal_file': forms.FileInput(attrs={'class': 'form-control'}),
            'work_book': forms.FileInput(attrs={'class': 'form-control'}),
            'no_criminal_record': forms.FileInput(attrs={'class': 'form-control'}),
            'diploma': forms.FileInput(attrs={'class': 'form-control'}),
            'autobiography': forms.FileInput(attrs={'class': 'form-control'}),
            'job_application': forms.FileInput(attrs={'class': 'form-control'}),
            'employment_contract': forms.FileInput(attrs={'class': 'form-control'}),
            'mj_notification': forms.FileInput(attrs={'class': 'form-control'}),
            'bar_notification': forms.FileInput(attrs={'class': 'form-control'}),
        }
