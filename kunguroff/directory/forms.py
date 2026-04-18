from django import forms
from .models import Organization, Region


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {
            'org_type':      forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'name':          forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Название организации'}),
            'region':        forms.Select(attrs={'class': 'form-select'}),
            'district':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Ленинский район, г. Ош'}),
            'address':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Улица, дом'}),
            'phone':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 312 000-000'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@example.gov.kg'}),
            'head_name':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'head_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Председатель суда'}),
            'website':       forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name', 'order']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Чуйская область'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
