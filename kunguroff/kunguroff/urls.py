"""
URL configuration for kunguroff project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib import admin
from .views import DashboardView, user_logout
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import DashboardView
from django.contrib.auth import views as auth_views


urlpatterns = [
    # set_language должен быть доступен БЕЗ префикса языка
    path("i18n/", include("django.conf.urls.i18n")),

    # admin без /ky/ и /en/
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", user_logout, name="logout"),

    path("cases/", include("cases.urls")),
    path("clients/", include("clients.urls")),
    path("finance/", include("finance.urls")),
    path("calendar/", include("calendar1.urls")),
    path("ratings/", include("ratings.urls")),

    path("", include("public.urls")),

    prefix_default_language=False,  # ru без /ru/, ky/en с /ky/ и /en/
)


# urlpatterns = [
#     path('admin/', admin.site.urls),
    

#     path("i18n/", include("django.conf.urls.i18n")),  # для set_language
#     path('dashboard/', DashboardView.as_view(), name='dashboard'),
#     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('logout/', user_logout, name='logout'),
#     path('cases/', include('cases.urls')),
#     path('clients/', include('clients.urls')),
#     # path('users/', include('users.urls')),
#     path('finance/', include('finance.urls')),
#     path('calendar/', include('calendar1.urls')),
#     path('ratings/', include('ratings.urls')),
#     # path('users/', include('users.urls')),
# ]
# urlpatterns += i18n_patterns(
#     path("", include("public.urls")),
#     prefix_default_language=False,  # ru без префикса, ky/en с префиксом
# )
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)