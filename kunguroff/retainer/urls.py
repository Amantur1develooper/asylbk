from django.urls import path
from . import views

app_name = 'retainer'

urlpatterns = [
    path('',                                        views.subscriber_list,     name='list'),
    path('add/',                                    views.subscriber_create,   name='subscriber_create'),
    path('<int:pk>/',                               views.subscriber_detail,   name='detail'),
    path('<int:pk>/edit/',                          views.subscriber_edit,     name='subscriber_edit'),

    path('<int:subscriber_pk>/subscription/add/',   views.subscription_create, name='subscription_create'),
    path('subscription/<int:pk>/edit/',             views.subscription_edit,   name='subscription_edit'),

    path('subscription/<int:subscription_pk>/payment/add/',  views.payment_create,   name='payment_create'),
    path('payment/<int:pk>/delete/',                         views.payment_delete,   name='payment_delete'),

    path('subscription/<int:subscription_pk>/service/add/',  views.service_create,   name='service_create'),
    path('service/<int:pk>/delete/',                         views.service_delete,   name='service_delete'),

    path('subscription/<int:subscription_pk>/document/upload/', views.document_upload, name='document_upload'),
    path('document/<int:pk>/delete/',                           views.document_delete, name='document_delete'),
]
