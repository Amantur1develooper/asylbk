from django import forms
from .models import Case, CaseCategory, CaseDocument, CaseParticipant, CaseStage
from clients.models import Trustor 
from django.contrib.auth import get_user_model

User = get_user_model()
# forms.py
# cases/forms.py
from django import forms
# from trustors.models import Trustor  # поправь путь при необходимости

class CaseParticipantForm(forms.ModelForm):
    class Meta:
        model = CaseParticipant
        fields = ['trustor', 'role', 'main_participant', 'representation_basis', 'powers_details']
        widgets = {
            'trustor': forms.Select(attrs={
                'class': 'form-select js-trustor',
                'data-placeholder': 'Начните вводить имя доверителя...'
            }),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'main_participant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'representation_basis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'powers_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def has_field(model, name):
            try:
                model._meta.get_field(name)
                return True
            except Exception:
                return False

        qs = Trustor.objects.all()
        if all(has_field(Trustor, f) for f in ['last_name', 'first_name', 'middle_name']):
            qs = qs.order_by('last_name', 'first_name', 'middle_name')
        elif all(has_field(Trustor, f) for f in ['last_name', 'first_name']):
            qs = qs.order_by('last_name', 'first_name')
        elif has_field(Trustor, 'last_name'):
            qs = qs.order_by('last_name')
        else:
            qs = qs.order_by('id')

        # применяем queryset
        self.fields['trustor'].queryset = qs

        # подпись опций: "Фамилия Имя Отчество — телефон"
        def label(obj):
            parts = [
                getattr(obj, 'last_name', None),
                getattr(obj, 'first_name', None),
                getattr(obj, 'middle_name', None),
            ]
            fio = " ".join([p for p in parts if p])
            phone = getattr(obj, 'phone', None)
            return f"{fio}{(' — ' + phone) if phone else ''}" or str(obj)

        self.fields['trustor'].label_from_instance = label

# cases/forms.py
from django import forms
from .models import Case, CaseStage, CaseCategory, User  # проверь импорты

class CaseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=CaseCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_category',
            # убираем несуществующую функцию loadStagesAndRoles
            'onchange': 'loadStages(this.value);'
        }),
        label="Категория дела*"
    )

    current_stage = forms.ModelChoiceField(
        queryset=CaseStage.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_current_stage'}),
        label="Текущий этап"
    )

    responsible_lawyer = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role__in=['lawyer', 'advocate']).order_by('last_name', 'first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'data-placeholder': 'Выберите ответственных юристов...',
            'style': 'width: 100%'
        }),
        label="Ответственные юристы/адвокаты"
    )

    class Meta:
        model = Case
        fields = [
            'title', 'description', 'category', 'responsible_lawyer',
            'manager', 'current_stage', 'status', 'contract_amount',
            'court_name', 'case_number', 'judge_name'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название дела'}),
            'contract_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Полная стоимость дела (100%)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Подробное описание дела...'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Название дела*',
            'description': 'Описание',
            'category': 'Категория дела*',
            'manager': 'Менеджер',
            'status': 'Статус*',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['title'].required = True
        self.fields['category'].required = True
        self.fields['status'].required = True

        if user and user.role in ['lawyer', 'advocate']:
            self.fields['responsible_lawyer'].initial = [user]

        # менеджеры
        self.fields['manager'].queryset = User.objects.filter(
            role__in=['manager', 'director', 'deputy_director']
        )

        # 1) Редактирование — подставить этапы категории инстанса
        if self.instance and self.instance.pk and self.instance.category_id:
            self.fields['current_stage'].queryset = CaseStage.objects.filter(
                category_id=self.instance.category_id
            ).order_by('order')
            if self.instance.current_stage_id:
                self.fields['current_stage'].initial = self.instance.current_stage

        # 2) Создание/POST — подставить этапы выбранной категории из self.data
        if 'category' in self.data:
            try:
                cat_id = int(self.data.get('category')) if self.data.get('category') else None
            except (TypeError, ValueError):
                cat_id = None

            if cat_id:
                qs = CaseStage.objects.filter(category_id=cat_id).order_by('order')
                self.fields['current_stage'].queryset = qs
                # Если пользователь ещё не выбрал этап — предложим первый
                if not self.data.get('current_stage') and qs.exists():
                    self.fields['current_stage'].initial = qs.first()

# class CaseForm(forms.ModelForm):
#     category = forms.ModelChoiceField(
#         queryset=CaseCategory.objects.all(),
#         widget=forms.Select(attrs={
#             'class': 'form-select',
#             'id': 'id_category',
#             'onchange': 'loadStagesAndRoles(this.value);'
#         }),
#         label="Категория дела*"
#     )

#     current_stage = forms.ModelChoiceField(
#         queryset=CaseStage.objects.none(),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_current_stage'}),
#         label="Текущий этап"
#     )

#     # ИЗМЕНЕНИЕ: Заменяем responsible_lawyer на responsible_lawyer
#     responsible_lawyer = forms.ModelMultipleChoiceField(
#         queryset=User.objects.filter(role__in=['lawyer', 'advocate']).order_by('last_name', 'first_name'),
#         required=False,
#         widget=forms.SelectMultiple(attrs={
#             'class': 'form-select select2-multiple',
#             'data-placeholder': 'Выберите ответственных юристов...',
#             'style': 'width: 100%'
#         }),
#         label="Ответственные юристы/адвокаты"
#     )

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
#             'title', 'description', 'category', 'responsible_lawyer',  # ИЗМЕНЕНИЕ
#             'manager', 'current_stage', 'status', 'contract_amount',  # НОВОЕ поле в форме
#             'court_name', 'case_number', 'judge_name'
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Введите название дела'
#             }),
#             'contract_amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01',
#                 'placeholder': 'Полная стоимость дела (100%)',
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control', 
#                 'rows': 4,
#                 'placeholder': 'Подробное описание дела...'
#             }),
#             'manager': forms.Select(attrs={'class': 'form-select'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#         }
#         labels = {
#             'title': 'Название дела*',
#             'description': 'Описание',
#             'category': 'Категория дела*',
#             'manager': 'Менеджер',
#             'status': 'Статус*',
#         }

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)

#         # ДОБАВЛЕНО: Устанавливаем обязательные поля
#         self.fields['title'].required = True
#         self.fields['category'].required = True
#         self.fields['status'].required = True

#         if user:
#             # Для юристов/адвокатов автоматически выбираем текущего пользователя
#             if user.role in ['lawyer', 'advocate']:
#                 self.fields['responsible_lawyer'].initial = [user]
            
#             # Настройка менеджера
#             if user.role in ['manager', 'director', 'deputy_director', 'admin']:
#                 self.fields['manager'].queryset = User.objects.filter(
#                     role__in=['manager', 'director', 'deputy_director']
#                 )
#             else:
#                 self.fields['manager'].queryset = User.objects.filter(
#                     role__in=['manager', 'director', 'deputy_director']
#                 )

#         # Если редактируем существующее дело
#         if self.instance and self.instance.pk and self.instance.category:
#             self.fields['current_stage'].queryset = CaseStage.objects.filter(
#                 category=self.instance.category
#             ).order_by('order')


#             if self.instance.current_stage:
#                 self.fields['current_stage'].initial = self.instance.current_stage
                       

 
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