from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from .models import Subscriber, Subscription, SubscriptionPayment, SubscriptionService, SubscriptionDocument
from .forms import SubscriberForm, SubscriptionForm, PaymentForm, ServiceForm, DocumentForm


def _can_manage(user):
    return user.is_superuser or user.role in (
        'manager', 'director', 'deputy_director', 'managing_partner_advocate',
        'lawyer', 'advocate', 'accountant',
    )


# ── Список абонентов ──────────────────────────────────────────────────────────
@login_required
def subscriber_list(request):
    q   = request.GET.get('q', '').strip()
    typ = request.GET.get('type', '')
    qs  = Subscriber.objects.prefetch_related('subscriptions').order_by('full_name')
    if q:
        qs = qs.filter(full_name__icontains=q)
    if typ:
        qs = qs.filter(client_type=typ)
    return render(request, 'retainer/subscriber_list.html', {
        'subscribers': qs,
        'q': q,
        'type': typ,
    })


# ── Создать абонента ──────────────────────────────────────────────────────────
@login_required
def subscriber_create(request):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    form = SubscriberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Абонент добавлен.')
        return redirect('retainer:list')
    return render(request, 'retainer/subscriber_form.html', {'form': form, 'action': 'Новый абонент'})


# ── Редактировать абонента ────────────────────────────────────────────────────
@login_required
def subscriber_edit(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    subscriber = get_object_or_404(Subscriber, pk=pk)
    form = SubscriberForm(request.POST or None, instance=subscriber)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Данные обновлены.')
        return redirect('retainer:detail', pk=pk)
    return render(request, 'retainer/subscriber_form.html', {
        'form': form, 'action': 'Редактировать абонента', 'subscriber': subscriber,
    })


# ── Карточка абонента (договоры, услуги, документы) ──────────────────────────
@login_required
def subscriber_detail(request, pk):
    subscriber    = get_object_or_404(Subscriber, pk=pk)
    subscriptions = subscriber.subscriptions.prefetch_related('payments', 'services', 'documents').all()
    return render(request, 'retainer/subscriber_detail.html', {
        'subscriber':    subscriber,
        'subscriptions': subscriptions,
        'can_manage':    _can_manage(request.user),
    })


# ── Добавить договор ──────────────────────────────────────────────────────────
@login_required
def subscription_create(request, subscriber_pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:detail', pk=subscriber_pk)
    subscriber = get_object_or_404(Subscriber, pk=subscriber_pk)
    form = SubscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.subscriber = subscriber
        sub.save()
        messages.success(request, 'Договор добавлен.')
        return redirect('retainer:detail', pk=subscriber_pk)
    return render(request, 'retainer/subscription_form.html', {
        'form': form, 'subscriber': subscriber, 'action': 'Новый договор',
    })


# ── Редактировать договор ─────────────────────────────────────────────────────
@login_required
def subscription_edit(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    subscription = get_object_or_404(Subscription, pk=pk)
    form = SubscriptionForm(request.POST or None, instance=subscription)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Договор обновлён.')
        return redirect('retainer:detail', pk=subscription.subscriber_id)
    return render(request, 'retainer/subscription_form.html', {
        'form': form, 'subscriber': subscription.subscriber,
        'subscription': subscription, 'action': 'Редактировать договор',
    })


# ── Добавить платёж ───────────────────────────────────────────────────────────
@login_required
def payment_create(request, subscription_pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    subscription = get_object_or_404(Subscription, pk=subscription_pk)
    form = PaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.subscription = subscription
        payment.created_by   = request.user
        payment.save()
        messages.success(request, 'Платёж записан.')
        return redirect('retainer:detail', pk=subscription.subscriber_id)
    return render(request, 'retainer/payment_form.html', {
        'form': form, 'subscription': subscription,
    })


# ── Удалить платёж ────────────────────────────────────────────────────────────
@login_required
def payment_delete(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    payment = get_object_or_404(SubscriptionPayment, pk=pk)
    subscriber_pk = payment.subscription.subscriber_id
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Платёж удалён.')
    return redirect('retainer:detail', pk=subscriber_pk)


# ── Добавить услугу ───────────────────────────────────────────────────────────
@login_required
def service_create(request, subscription_pk):
    subscription = get_object_or_404(Subscription, pk=subscription_pk)
    form = ServiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        svc = form.save(commit=False)
        svc.subscription = subscription
        svc.save()
        messages.success(request, 'Услуга добавлена.')
        return redirect('retainer:detail', pk=subscription.subscriber_id)
    return render(request, 'retainer/service_form.html', {
        'form': form, 'subscription': subscription,
    })


# ── Удалить услугу ────────────────────────────────────────────────────────────
@login_required
def service_delete(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    service = get_object_or_404(SubscriptionService, pk=pk)
    subscriber_pk = service.subscription.subscriber_id
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Запись об услуге удалена.')
    return redirect('retainer:detail', pk=subscriber_pk)


# ── Загрузить документ ────────────────────────────────────────────────────────
@login_required
def document_upload(request, subscription_pk):
    subscription = get_object_or_404(Subscription, pk=subscription_pk)
    form = DocumentForm(subscription=subscription, data=request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.subscription = subscription
        doc.uploaded_by  = request.user
        doc.save()
        messages.success(request, 'Документ загружен.')
        return redirect('retainer:detail', pk=subscription.subscriber_id)
    return render(request, 'retainer/document_form.html', {
        'form': form, 'subscription': subscription,
    })


# ── Удалить документ ─────────────────────────────────────────────────────────
@login_required
def document_delete(request, pk):
    if not _can_manage(request.user):
        messages.error(request, 'Нет доступа.')
        return redirect('retainer:list')
    doc = get_object_or_404(SubscriptionDocument, pk=pk)
    subscriber_pk = doc.subscription.subscriber_id
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Документ удалён.')
    return redirect('retainer:detail', pk=subscriber_pk)
