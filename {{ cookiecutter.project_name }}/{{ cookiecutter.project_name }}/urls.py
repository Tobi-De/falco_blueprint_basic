from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import TemplateView
from falco import views as falco_views
from falco.urls import errors_views
from health_check.views import MainView
from allauth.account.decorators import secure_admin_login

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path(".well-known/security.txt", falco_views.security_txt),
    path("robots.txt", falco_views.robots_txt),
    path("", include("falco_ui.urls")),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("health/", MainView.as_view()),
    path("accounts/", include("allauth.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
        *errors_views,
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
