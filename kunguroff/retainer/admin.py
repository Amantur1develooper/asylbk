from django.contrib import admin
from .models import Subscriber, Subscription, SubscriptionPayment, SubscriptionService, SubscriptionDocument


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ('contract_number', 'start_date', 'end_date', 'monthly_fee', 'status', 'responsible')
    show_change_link = True


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'client_type', 'phone', 'email', 'created_at')
    list_filter   = ('client_type',)
    search_fields = ('full_name', 'phone', 'email', 'inn')
    inlines       = [SubscriptionInline]


class SubscriptionPaymentInline(admin.TabularInline):
    model  = SubscriptionPayment
    extra  = 0
    fields = ('date', 'period', 'amount', 'note', 'created_by')


class SubscriptionServiceInline(admin.TabularInline):
    model  = SubscriptionService
    extra  = 0
    fields = ('date', 'service_type', 'description', 'lawyer', 'hours')
    show_change_link = True


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('subscriber', 'contract_number', 'monthly_fee', 'status', 'start_date', 'end_date')
    list_filter   = ('status',)
    search_fields = ('subscriber__full_name', 'contract_number')
    inlines       = [SubscriptionPaymentInline, SubscriptionServiceInline]


@admin.register(SubscriptionService)
class SubscriptionServiceAdmin(admin.ModelAdmin):
    list_display  = ('subscription', 'date', 'service_type', 'lawyer')
    list_filter   = ('service_type',)
    search_fields = ('description', 'subscription__subscriber__full_name')
