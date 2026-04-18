from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from .views import DashboardView, user_logout, SmartLoginView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", SmartLoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),

    path("cases/", include("cases.urls")),
    path("clients/", include("clients.urls")),
    path("finance/", include("finance.urls")),
    path("calendar/", include("calendar1.urls")),
    path("ratings/", include("ratings.urls")),
    path("grafik/", include("schedule.urls")),
    path("hr/", include("hr.urls")),
    path("directory/", include("directory.urls")),

    path("", include("public.urls")),

    prefix_default_language=False,
)

admin.site.site_header = "Администрирование Kunguroff"
admin.site.site_title = "Kunguroff"
admin.site.index_title = "Панель управления"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
