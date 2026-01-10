from django import forms
from .models import ConsultationRequest

from django import forms
from .models import ConsultationRequest

class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ["name", "phone", "email", "topic", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control form-control-lg kp-input",
                "placeholder": "Ваше имя",
                "autocomplete": "name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control form-control-lg kp-input",
                "placeholder": "+996 ___ ___ ___",
                "autocomplete": "tel",
                "inputmode": "tel",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control form-control-lg kp-input",
                "placeholder": "example@mail.com (необязательно)",
                "autocomplete": "email",
            }),
            "topic": forms.TextInput(attrs={
                "class": "form-control form-control-lg kp-input",
                "placeholder": "Тема обращения (необязательно)",
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control kp-input",
                "rows": 4,
                "placeholder": "Коротко опишите ситуацию (необязательно)",
            }),
        }

