from django import forms
from .models import Case, CaseCategory, CaseDocument, CaseParticipant, CaseStage
from clients.models import Trustor 
from django.contrib.auth import get_user_model

User = get_user_model()

class CaseParticipantForm(forms.ModelForm):
    """Форма для добавления участника дела"""
    
    class Meta:
        model = CaseParticipant
        fields = ['trustor', 'role', 'main_participant', 'representation_basis', 'powers_details']
        widgets = {
            'trustor': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'main_participant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'representation_basis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'powers_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
class CaseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=CaseCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_category',
            'onchange': 'loadStagesAndRoles(this.value);'
        }),
        label="Категория дела"
    )

    current_stage = forms.ModelChoiceField(
        queryset=CaseStage.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_current_stage'}),
        label="Текущий этап"
    )

    court_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Наименование суда"
    )
    case_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Номер дела в суде"
    )
    judge_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="ФИО судьи"
    )

    class Meta:
        model = Case
        fields = [
            'title', 'description', 'category', 'responsible_lawyer',
            'manager', 'current_stage', 'status', 'court_name', 'case_number', 'judge_name'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsible_lawyer': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.role in ['lawyer', 'advocate']:
                self.fields['responsible_lawyer'].queryset = User.objects.filter(pk=user.pk)
                self.fields['responsible_lawyer'].initial = user
                self.fields['responsible_lawyer'].empty_label = None
            elif user.role in ['manager', 'director', 'deputy_director', 'admin']:
                self.fields['responsible_lawyer'].queryset = User.objects.filter(
                    role__in=['lawyer', 'advocate']
                )

        # Если редактируем существующее дело
        if self.instance and self.instance.pk and self.instance.category:
            self.fields['current_stage'].queryset = CaseStage.objects.filter(
                category=self.instance.category
            ).order_by('order')

            # 🔹 вот это добавляем
            if self.instance.current_stage:
                self.fields['current_stage'].initial = self.instance.current_stage
        
# class CaseForm(forms.ModelForm):
#     category = forms.ModelChoiceField(
#         queryset=CaseCategory.objects.all(),
#         widget=forms.Select(attrs={
#             'class': 'form-select',
#             'id': 'id_category',
#             'onchange': 'loadStagesAndRoles(this.value);'
#         }),
#         label="Категория дела"
#     )
    
#     current_stage = forms.ModelChoiceField(
#         queryset=CaseStage.objects.none(),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_current_stage'}),
#         label="Текущий этап"
#     )
    
#     # Поля судебной информации
#     court_name = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         label="Наименование суда"
#     )
#     case_number = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         label="Номер дела в суде"
#     )
#     judge_name = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         label="ФИО судьи"
#     )
    
#     class Meta:
#         model = Case
#         fields = [
#             'title', 'description', 'category', 'responsible_lawyer', 
#             'manager', 'current_stage', 'status', 'court_name', 'case_number', 'judge_name'
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'responsible_lawyer': forms.Select(attrs={'class': 'form-select'}),
#             'manager': forms.Select(attrs={'class': 'form-select'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
        
#         if user:
#             # Ограничиваем выбор доверителей в зависимости от роли
#             if user.role in ['lawyer', 'advocate']:
#                 self.fields['responsible_lawyer'].queryset = User.objects.filter(pk=user.pk)
#                 self.fields['responsible_lawyer'].initial = user
#                 self.fields['responsible_lawyer'].empty_label = None
            
#             elif user.role in ['manager', 'director', 'deputy_director', 'admin']:
#                 self.fields['responsible_lawyer'].queryset = User.objects.filter(
#                     role__in=['lawyer', 'advocate']
#                 )
        
#         # Если редактируем существующее дело
#         if self.instance and self.instance.pk and self.instance.category:
#             self.fields['current_stage'].queryset = CaseStage.objects.filter(
#                 category=self.instance.category
#             ).order_by('order')
#             if self.instance.current_stage:
#                 self.fields['current_stage'].initial = self.instance.current_stage

        # if self.instance and self.instance.pk and self.instance.category:
        #     self.fields['current_stage'].queryset = CaseStage.objects.filter(
        #         category=self.instance.category
        #     ).order_by('order')
 
class CaseDocumentForm(forms.ModelForm):
    class Meta:
        model = CaseDocument
        fields = ['stage', 'field', 'text_value', 'file_value', 'date_value']
        widgets = {
            'stage': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_document_stage',
                'onchange': 'loadFields(this.value);'
            }),
            'field': forms.Select(attrs={'class': 'form-select', 'id': 'id_document_field'}),
            'text_value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите текстовое значение'
            }),
            'file_value': forms.FileInput(attrs={'class': 'form-control'}),
            'date_value': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'stage': 'Этап',
            'field': 'Поле',
            'text_value': 'Текстовое значение',
            'file_value': 'Файл',
            'date_value': 'Дата',
        }
    
    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case', None)
        super().__init__(*args, **kwargs)
        
        if self.case:
            # Ограничиваем выбор этапов и полей текущей категорией дела
            self.fields['stage'].queryset = CaseStage.objects.filter(
                category=self.case.category
            ).order_by('order')
            
            # Поля будут загружаться через AJAX
            self.fields['field'].queryset = self.fields['field'].queryset.none()
    
    def clean(self):
        cleaned_data = super().clean()
        stage = cleaned_data.get('stage')
        field = cleaned_data.get('field')
        text_value = cleaned_data.get('text_value')
        file_value = cleaned_data.get('file_value')
        date_value = cleaned_data.get('date_value')
        
        # Проверяем, что поле принадлежит этапу
        if stage and field and field.stage != stage:
            raise forms.ValidationError({
                'field': 'Выбранное поле не принадлежит выбранному этапу'
            })
        
        # Проверяем, что заполнено значение в соответствии с типом поля
        if field:
            if field.field_type == 'text' and not text_value:
                raise forms.ValidationError({
                    'text_value': 'Это поле обязательно для заполнения'
                })
            elif field.field_type == 'file' and not file_value:
                raise forms.ValidationError({
                    'file_value': 'Это поле обязательно для заполнения'
                })
            elif field.field_type == 'date' and not date_value:
                raise forms.ValidationError({
                    'date_value': 'Это поле обязательно для заполнения'
                })
        
        # Проверяем, что документ с таким полем и этапом еще не существует
        if self.case and stage and field:
            existing_document = CaseDocument.objects.filter(
                case=self.case, stage=stage, field=field
            ).first()
            
            if existing_document and (not self.instance or self.instance != existing_document):
                raise forms.ValidationError(
                    'Документ для этого поля и этапа уже существует'
                )
        
        return cleaned_data