from django import forms
from django.utils import timezone
from .models import Subscriber, Subscription, SubscriptionPayment, SubscriptionService, SubscriptionDocument


class SubscriberForm(forms.ModelForm):
    class Meta:
        model  = Subscriber
        fields = ['client_type', 'full_name', 'contact_person', 'inn', 'phone', 'email', 'address', 'notes']
        widgets = {
            'client_type':    forms.Select(attrs={'class': 'form-select'}),
            'full_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО или название организации'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Контактное лицо (для юр. лиц)'}),
            'inn':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 ...'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес'}),
            'notes':          forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model  = Subscription
        fields = ['contract_number', 'start_date', 'end_date', 'monthly_fee', 'status', 'responsible', 'notes']
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '№ договора'}),
            'start_date':      forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':        forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_fee':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status':          forms.Select(attrs={'class': 'form-select'}),
            'responsible':     forms.Select(attrs={'class': 'form-select'}),
            'notes':           forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')


class PaymentForm(forms.ModelForm):
    class Meta:
        model  = SubscriptionPayment
        fields = ['date', 'period', 'amount', 'note']
        widgets = {
            'date':   forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2026-05'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'note':   forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields['date'].initial = today
        self.fields['period'].initial = f'{today.year}-{today.month:02d}'


class ServiceForm(forms.ModelForm):
    class Meta:
        model  = SubscriptionService
        fields = ['date', 'service_type', 'description', 'lawyer', 'hours']
        widgets = {
            'date':         forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'description':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                  'placeholder': 'Опишите суть оказанной услуги, результат...'}),
            'lawyer':       forms.Select(attrs={'class': 'form-select'}),
            'hours':        forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localdate()


class DocumentForm(forms.ModelForm):
    class Meta:
        model  = SubscriptionDocument
        fields = ['name', 'service', 'file']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название документа'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'file':    forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, subscription=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if subscription:
            self.fields['service'].queryset = subscription.services.all()
        self.fields['service'].required = False
        self.fields['service'].empty_label = '— без привязки к услуге —'
