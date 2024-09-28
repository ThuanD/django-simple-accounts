from django.contrib.auth import views
from django.urls import path, reverse_lazy
from django.views.i18n import JavaScriptCatalog

from .settings import acc_settings
from .views import (
    MyLoginView,
    HomeView,
    ProfileView,
)

app_name = "accounts"
urlpatterns = [
    path("",
         HomeView.as_view(
             template_name=acc_settings.HOME_TEMPLATE),
         name="home"),
    path("login/",
         MyLoginView.as_view(
             template_name=acc_settings.LOGIN_TEMPLATE),
         name="login"),
    path("logout/",
         views.LogoutView.as_view(
             template_name=acc_settings.LOGOUT_TEMPLATE),
         name="logged_out"),
    path("profile/<pk>/change/",
         ProfileView.as_view(
             template_name=acc_settings.PROFILE_TEMPLATE),
         name="profile"),
    path("profile/<pk>/password/",
         views.PasswordChangeView.as_view(
             template_name=acc_settings.PASSWORD_CHANGE_TEMPLATE,
             success_url=reverse_lazy("accounts:password_change_done"), ),
         name="password"),
    path("password_change/",
         views.PasswordChangeView.as_view(
             template_name=acc_settings.PASSWORD_CHANGE_TEMPLATE,
             success_url=reverse_lazy("accounts:password_change_done"), ),
         name="password_change"),
    path("password_change/done/",
         views.PasswordChangeDoneView.as_view(
             template_name=acc_settings.PASSWORD_CHANGE_DONE_TEMPLATE),
         name="password_change_done", ),
    path("password_reset/",
         views.PasswordResetView.as_view(
             email_template_name=acc_settings.PASSWORD_RESET_EMAIL_TEMPLATE,
             success_url=reverse_lazy("accounts:password_reset_done"),
             template_name=acc_settings.PASSWORD_RESET_TEMPLATE, ),
         name="password_reset"),
    path("password_reset/done/",
         views.PasswordResetDoneView.as_view(
             template_name=acc_settings.PASSWORD_RESET_DONE_TEMPLATE),
         name="password_reset_done", ),
    path("reset/<uidb64>/<token>/",
         views.PasswordResetConfirmView.as_view(
             template_name=acc_settings.PASSWORD_RESET_CONFIRM_TEMPLATE,
             success_url=reverse_lazy("accounts:password_reset_complete"), ),
         name="password_reset_confirm", ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(
            template_name=acc_settings.PASSWORD_RESET_COMPLETE_TEMPLATE),
        name="password_reset_complete", ),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="jsi18n"),
]
