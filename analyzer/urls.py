
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("history/", views.history, name="history"),
    path(
        "history/delete/<int:report_id>/",
        views.delete_report,
        name="delete_report",
    ),
    path(
        "history/download/<int:report_id>/",
        views.download_report_pdf,
        name="download_report_pdf",
    ),
    path(
        "register/",
        views.register,
        name="register",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
