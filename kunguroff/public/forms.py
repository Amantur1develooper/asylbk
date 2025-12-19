from django import forms
from .models import ConsultationRequest

class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ["name", "phone", "email", "topic", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }
