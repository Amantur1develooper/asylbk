from core.permissions import LawyerRequiredMixin, OwnerOrManagerMixin, DirectorRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Case, CaseCategory, CaseStage, CaseDocument
from .forms import CaseForm, CaseDocumentForm
from django.shortcuts import render, get_object_or_404, redirect
from finance.models import CaseFinance, CaseFinanceShare

# Список всех дел
class CaseListView(LawyerRequiredMixin,DirectorRequiredMixin, ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 20
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Фильтрация по роли пользователя
        user = self.request.user
        if user.role in ['lawyer', 'advocate']:
            # ИЗМЕНЕНИЕ: Юристы видят дела, где они входят в ответственные
            return Case.objects.filter(responsible_lawyer=user)
        elif user.role == 'manager':
            # Менеджеры видят дела своей команды
            
            return Case.objects.all()
        else:
            # Директора и админы видят все дела
            return Case.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем категории для фильтрации
        context['categories'] = CaseCategory.objects.all()
        return context
    
    
# class CaseListView(LawyerRequiredMixin,ListView):
#     model = Case
#     template_name = 'cases/case_list.html'
#     context_object_name = 'cases'
#     paginate_by = 20
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get_queryset(self):
#         # Фильтрация по роли пользователя
#         user = self.request.user
#         if user.role in ['lawyer', 'advocate']:
#             # Юристы видят только свои дела
#             return Case.objects.filter(responsible_lawyer=user)
#         elif user.role == 'manager':
#             # Менеджеры видят дела своей команды
#             # Здесь нужно доработать логику определения команды
#             return Case.objects.all()
#         else:
#             # Директора и админы видят все дела
#             return Case.objects.all()
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Добавляем категории для фильтрации
#         context['categories'] = CaseCategory.objects.all()
#         return context

# Детальная информация о деле
class CaseDetailView(DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Проверка прав доступа
        user = self.request.user
        if user.role in ['lawyer', 'advocate']:
            # ИЗМЕНЕНИЕ: Фильтруем по связи ManyToMany
            return Case.objects.filter(responsible_lawyer=user)
        return Case.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем форму для загрузки документов
        context['document_form'] = CaseDocumentForm()
        # Добавляем список документов по этапам
        context['documents_by_stage'] = {}
        for stage in self.object.category.stages.all():
            context['documents_by_stage'][stage] = CaseDocument.objects.filter(
                case=self.object, stage=stage
            )
        return context

# class CaseDetailView(DetailView):
#     model = Case
#     template_name = 'cases/case_detail.html'
#     context_object_name = 'case'
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get_queryset(self):
#         # Проверка прав доступа
#         user = self.request.user
#         if user.role in ['lawyer', 'advocate']:
#             return Case.objects.filter(responsible_lawyer=user)
#         return Case.objects.all()
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Добавляем форму для загрузки документов
#         context['document_form'] = CaseDocumentForm()
#         # Добавляем список документов по этапам
#         context['documents_by_stage'] = {}
#         for stage in self.object.category.stages.all():
#             context['documents_by_stage'][stage] = CaseDocument.objects.filter(
#                 case=self.object, stage=stage
#             )
#         return context

# Создание нового дела
# class CaseCreateView(LawyerRequiredMixin, CreateView):
#     model = Case
#     form_class = CaseForm
#     template_name = 'cases/case_form.html'
#     success_url = reverse_lazy('cases:case_list')
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         # Только определенные роли могут создавать дела
#         allowed_roles = ['manager', 'lawyer', 'advocate', 'director', 'deputy_director']
#         if self.request.user.role not in allowed_roles:
#             return redirect('permission_denied')
#         return super().dispatch(*args, **kwargs)
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
    
#     def form_valid(self, form):
#         # Сохраняем объект сначала
#         response = super().form_valid(form)
        
#         # ИЗМЕНЕНИЕ: Если пользователь - юрист/адвокат и он не выбран в форме,
#         # автоматически добавляем его в ответственные
#         if self.request.user.role in ['lawyer', 'advocate']:
#             if self.request.user not in self.object.responsible_lawyer.all():
#                 self.object.responsible_lawyer.add(self.request.user)
        
#         # Устанавливаем первый этап в качестве текущего
#         category = form.instance.category
#         first_stage = category.stages.order_by('order').first()
#         if first_stage:
#             self.object.current_stage = first_stage
#             self.object.save()
        
#         # Добавляем сообщение об успехе
#         messages.success(self.request, f'Дело "{self.object.title}" успешно создано.')
        
#         return response
class CaseCreateView(LawyerRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'
    success_url = reverse_lazy('cases:case_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Только определенные роли могут создавать дела
        allowed_roles = ['manager', 'lawyer', 'advocate', 'director', 'deputy_director']
        if self.request.user.role not in allowed_roles:
            return redirect('permission_denied')
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Сохраняем дело
        response = super().form_valid(form)

        # Если пользователь - юрист/адвокат и он не выбран в форме,
        # автоматически добавляем его в ответственные
        if self.request.user.role in ['lawyer', 'advocate']:
            if self.request.user not in self.object.responsible_lawyer.all():
                self.object.responsible_lawyer.add(self.request.user)

        # Финансовая карточка создаётся сигналом post_save(Case),
        # но подстрахуемся — если её нет, создадим вручную
        finance, created = CaseFinance.objects.get_or_create(
            case=self.object,
            defaults={
                'contract_amount': self.object.contract_amount or 0,
                'paid_amount': 0,
            }
        )

        # Если по делу есть ответственные юристы и пока нет долей — распределяем 70% поровну
        if not finance.shares.exists():
            from decimal import Decimal
            lawyers = self.object.responsible_lawyer.all()
            count = lawyers.count()
            if count > 0:
                base = (Decimal('100.00') / count).quantize(Decimal('0.01'))
                remainder = Decimal('100.00') - base * count

                for idx, lawyer in enumerate(lawyers):
                    percent = base + remainder if idx == 0 else base
                    CaseFinanceShare.objects.create(
                        case_finance=finance,
                        employee=lawyer,
                        percent_of_pool=percent,
                    )
                finance.recalc_shares()

        messages.success(self.request, f'Дело "{self.object.title}" успешно создано.')
        return response


class CaseUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Проверка прав доступа
        case = self.get_object()
        user = self.request.user
        allowed_roles = ['manager', 'director', 'deputy_director']

        # Юристы могут редактировать только свои дела
        if user.role in ['lawyer', 'advocate'] and user not in case.responsible_lawyer.all():
            return redirect('permission_denied')

        # Менеджеры и директора могут редактировать все дела
        if user.role not in allowed_roles + ['lawyer', 'advocate']:
            return redirect('permission_denied')

        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases:case_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)

        # Обновляем сумму договора в финансовой карточке (если есть / создаём)
        finance, created = CaseFinance.objects.get_or_create(
            case=self.object,
            defaults={
                'contract_amount': self.object.contract_amount or 0,
                'paid_amount': 0,
            }
        )
        finance.contract_amount = self.object.contract_amount or 0
        finance.recalc_shares()
        finance.save()

        messages.success(self.request, f'Дело "{self.object.title}" успешно обновлено.')
        return response

# class CaseCreateView(LawyerRequiredMixin,CreateView):
#     model = Case
#     form_class = CaseForm
#     template_name = 'cases/case_form.html'
#     success_url = reverse_lazy('cases:case_list')
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         # Только определе нные роли могут создавать дела
#         allowed_roles = ['manager', 'lawyer', 'advocate', 'director', 'deputy_director']
#         if self.request.user.role not in allowed_roles:
#             return redirect('permission_denied')
#         return super().dispatch(*args, **kwargs)
    
#     def form_valid(self, form):
#         # Автоматически устанавливаем текущего пользователя как ответственного юриста
#         # если он юрист/адвокат
#         if self.request.user.role in ['lawyer', 'advocate']:
#             form.instance.responsible_lawyer = self.request.user
        
#         # Устанавливаем первый этап в качестве текущего
#         response = super().form_valid(form)
#         category = form.instance.category
#         first_stage = category.stages.order_by('order').first()
#         if first_stage:
#             form.instance.current_stage = first_stage
#             form.instance.save()
        
#         return response


# Редактирование дела
# class CaseUpdateView(OwnerOrManagerMixin, UpdateView):
#     model = Case
#     form_class = CaseForm
#     template_name = 'cases/case_form.html'
    
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         # Проверка прав доступа
#         case = self.get_object()
#         user = self.request.user
#         allowed_roles = ['manager', 'director', 'deputy_director']
        
#         # ИЗМЕНЕНИЕ: Юристы могут редактировать только свои дела
#         if user.role in ['lawyer', 'advocate'] and user not in case.responsible_lawyer.all():
#             return redirect('permission_denied')
        
#         # Менеджеры и директора могут редактировать все дела
#         if user.role not in allowed_roles + ['lawyer', 'advocate']:
#             return redirect('permission_denied')
            
#         return super().dispatch(*args, **kwargs)
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
    
#     def get_success_url(self):
#         return reverse_lazy('cases:case_detail', kwargs={'pk': self.object.pk})
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         messages.success(self.request, f'Дело "{self.object.title}" успешно обновлено.')
#         return response


# Удаление дела
class CaseDeleteView(DirectorRequiredMixin, DeleteView):
    model = Case
    template_name = 'cases/case_confirm_delete.html'
    success_url = reverse_lazy('cases:case_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Только директора и зам.директора могут удалять дела
        user = self.request.user
        if user.role not in ['director', 'deputy_director']:
            return redirect('permission_denied')
        return super().dispatch(*args, **kwargs)

# Добавление документа к делу
class CaseDocumentCreateView(View):
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        case = get_object_or_404(Case, pk=kwargs['pk'])
        
        # Проверка прав доступа
        user = request.user
        # ИЗМЕНЕНИЕ: Проверяем через ManyToMany связь
        if user.role in ['lawyer', 'advocate'] and user not in case.responsible_lawyer.all():
            return redirect('permission_denied')
        
        form = CaseDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.case = case
            document.created_by = request.user
            document.save()
            
            # Пересчитываем прогресс дела
            case.calculate_progress()
            
            return redirect('cases:case_detail', pk=case.pk)
        
        # Если форма невалидна, возвращаемся к деталям дела с ошибками
        return render(request, 'cases/case_detail.html', {
            'case': case,
            'document_form': form,
            'documents_by_stage': CaseDocument.objects.filter(case=case).group_by_stage()
        })
# class CaseDocumentCreateView(View):
#     @method_decorator(login_required)
#     def post(self, request, *args, **kwargs):
#         case = get_object_or_404(Case, pk=kwargs['pk'])
        
#         # Проверка прав доступа
#         user = request.user
#         if user.role in ['lawyer', 'advocate'] and case.responsible_lawyer != user:
#             return redirect('permission_denied')
        
#         form = CaseDocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             document = form.save(commit=False)
#             document.case = case
#             document.created_by = request.user
#             document.save()
            
#             # Пересчитываем прогресс дела
#             case.calculate_progress()
            
#             return redirect('cases:case_detail', pk=case.pk)
        
#         # Если форма невалидна, возвращаемся к деталям дела с ошибками
#         return render(request, 'cases/case_detail.html', {
#             'case': case,
#             'document_form': form,
#             'documents_by_stage': CaseDocument.objects.filter(case=case).group_by_stage()
#         })

# AJAX-представление для получения этапов категории
class CategoryStagesView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category_id')
        stages = CaseStage.objects.filter(category_id=category_id).order_by('order')
        
        stages_data = []
        for stage in stages:
            stages_data.append({
                'id': stage.id,
                'name': stage.name,
                'order': stage.order
            })
        
        return JsonResponse({'stages': stages_data})
    
    
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

@require_GET
def ajax_load_stages(request):
    """AJAX-представление для загрузки этапов по категории"""
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    try:
        from .models import CaseStage
        stages = CaseStage.objects.filter(category_id=category_id).order_by('order')
        stages_data = [{
            'id': stage.id,
            'name': stage.name,
            'order': stage.order,
            'description': stage.description
        } for stage in stages]
        
        return JsonResponse({'stages': stages_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def ajax_load_stage_fields(request):
    """AJAX-представление для загрузки полей этапа"""
    stage_id = request.GET.get('stage_id')
    if not stage_id:
        return JsonResponse({'error': 'Stage ID is required'}, status=400)
    
    try:
        from .models import StageField
        fields = StageField.objects.filter(stage_id=stage_id).order_by('order')
        fields_data = [{
            'id': field.id,
            'name': field.name,
            'field_type': field.field_type,
            'is_required': field.is_required,
            'options': field.options.split(',') if field.options else []
        } for field in fields]
        
        return JsonResponse({'fields': fields_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def ajax_load_field_info(request, field_id):
    """AJAX-представление для загрузки информации о поле"""
    try:
        from .models import StageField
        field = get_object_or_404(StageField, id=field_id)
        
        field_data = {
            'id': field.id,
            'name': field.name,
            'field_type': field.field_type,
            'is_required': field.is_required,
            'options': field.options.split(',') if field.options else []
        }
        
        return JsonResponse(field_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def ajax_load_stages(request):
    """AJAX-представление для загрузки этапов по категории"""
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    try:
        from .models import CaseStage
        stages = CaseStage.objects.filter(category_id=category_id).order_by('order')
        stages_data = [{
            'id': stage.id,
            'name': stage.name,
            'order': stage.order,
            'description': stage.description
        } for stage in stages]
        
        return JsonResponse({'stages': stages_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
from django.http import JsonResponse



from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CaseParticipant, CaseParticipantRole
from .forms import CaseParticipantForm

class CaseParticipantCreateView(LawyerRequiredMixin, CreateView):
    model = CaseParticipant
    form_class = CaseParticipantForm
    template_name = 'cases/participant_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = get_object_or_404(Case, pk=self.kwargs['case_pk'])
        return context
    
    def form_valid(self, form):
        case = get_object_or_404(Case, pk=self.kwargs['case_pk'])
        form.instance.case = case
        
        # Если отмечаем как основного, снимаем отметку с других
        if form.cleaned_data.get('main_participant'):
            CaseParticipant.objects.filter(case=case, main_participant=True).update(main_participant=False)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('cases:case_detail', kwargs={'pk': self.kwargs['case_pk']})

class CaseParticipantUpdateView(OwnerOrManagerMixin, UpdateView):
    model = CaseParticipant
    form_class = CaseParticipantForm
    template_name = 'cases/participant_form.html'
    
    def form_valid(self, form):
        # Если отмечаем как основного, снимаем отметку с других
        if form.cleaned_data.get('main_participant'):
            CaseParticipant.objects.filter(
                case=form.instance.case, 
                main_participant=True
            ).exclude(pk=form.instance.pk).update(main_participant=False)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('cases:case_detail', kwargs={'pk': self.object.case.pk})

class CaseParticipantDeleteView(OwnerOrManagerMixin, DeleteView):
    model = CaseParticipant
    template_name = 'cases/participant_confirm_delete.html'
    context_object_name = 'participant'

    def get_success_url(self):
        return reverse_lazy('cases:case_detail', kwargs={'pk': self.object.case.pk})

def ajax_load_participant_roles(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    try:
        roles = CaseParticipantRole.objects.filter(category_id=category_id).order_by('order')
        roles_data = [{
            'id': role.id,
            'code': role.role_code,
            'name': role.role_name,
            'description': role.description
        } for role in roles]
        
        return JsonResponse({'roles': roles_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from .models import CaseDocument, Case

def user_can_edit_case(user, case: Case) -> bool:
    """Права: суперюзер / менеджер / любой из ответственных юристов."""
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    if case.manager_id == user.id:
        return True
    # ManyToMany — корректная проверка принадлежности
    if case.responsible_lawyer.filter(pk=user.pk).exists():
        return True
    return False


class CaseDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Удаление CaseDocument по связке (case_id, stage_id, field_id).
    Безопасно удаляет физический файл и пересчитывает прогресс дела.
    GET  -> страница подтверждения
    POST -> удаление и редирект на карточку дела
    """
    template_name = "cases/document_confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            CaseDocument,
            case_id=self.kwargs["case_id"],
            stage_id=self.kwargs["stage_id"],
            field_id=self.kwargs["field_id"],
        )

    # Проверка прав на основе связанного дела
    def test_func(self):
        doc = self.get_object()
        return user_can_edit_case(self.request.user, doc.case)

    def get(self, request, *args, **kwargs):
        doc = self.get_object()
        context = {
            "object": doc,
            "case": doc.case,
            "stage": doc.stage,
            "field": doc.field,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        doc = self.get_object()
        case = doc.case

        with transaction.atomic():
            # 1) Удаляем физический файл, если был загружен
            if doc.file_value:
                # save=False, чтобы не трогать БД повторно
                doc.file_value.delete(save=False)
            # 2) Удаляем сам документ
            doc.delete()
            # 3) Пересчитываем прогресс дела
            case.calculate_progress()

        messages.success(request, "Документ успешно удалён.")
        # Замените 'cases:detail' на ваш реальный name урла карточки дела
        return redirect(reverse("cases:case_detail", args=[case.pk]))
