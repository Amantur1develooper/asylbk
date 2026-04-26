from django import forms
from .models import KnowledgePost


class KnowledgePostForm(forms.ModelForm):
    class Meta:
        model  = KnowledgePost
        fields = ['title', 'category', 'body', 'is_pinned']
        widgets = {
            'title':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'body':     forms.Textarea(attrs={'class': 'form-control', 'rows': 10,
                                              'placeholder': 'Текст, описание, инструкция…'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title':     'Заголовок',
            'category':  'Категория',
            'body':      'Текст',
            'is_pinned': 'Закрепить запись',
        }
