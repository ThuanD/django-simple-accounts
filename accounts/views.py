from urllib.parse import quote as urlquote

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView

from .adapter import get_adapter
from .forms import ProfileForm
from .settings import acc_settings

User = get_user_model()
adapter = get_adapter()


class BaseView:
    site_title = acc_settings.SITE_TITLE
    site_header = acc_settings.SITE_HEADER
    errors = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=self.title,
            site_title=self.site_title,
            site_header=self.site_header,
            errors=self.errors,
        )
        return context


class MyLoginView(BaseView, LoginView):
    template_name = "accounts/login_form.html"
    redirect_authenticated_user = True
    title = _("Login")

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(acc_settings.LOGIN_REDIRECT_URL)


class HomeView(BaseView, TemplateView):
    name = "accounts"
    template_name = "accounts/home.html"
    title = _("Home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = {
            "subtitle": None,
            "messages": messages.get_messages(self.request),
            "app_list": adapter.get_app_list(self.request.user),
            "client_ip": adapter.get_client_ip(self.request),
            "ua_string": self.request.META["HTTP_USER_AGENT"],
            **(self.extra_context or {})
        }
        context.update(data)
        return context

    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileView(BaseView, UpdateView):
    template_name = "accounts/profile_form.html"
    title = _("Profile")
    model = User
    form_class = ProfileForm
    app_label = User._meta.app_label

    fieldsets = (
        (_('Identity'), {'fields': ('username', 'password')}),
        (_('Personal infomation'), {
            'classes': ['collapse'],
            'fields': ('first_name', 'last_name', 'email'),
        }),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
    )

    def get_object(self):
        return self.request.user

    def has_read_perm(self):
        return self.request.user.has_perm(f"{self.app_label}.view_user")

    def has_change_perm(self):
        return self.request.user.has_perm(f"{self.app_label}.change_user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fieldsets'] = self.fieldsets
        return context

    def get_success_url(self):
        opts = self.object._meta  # noqa
        current_path = urlquote(self.request.path)
        msg_dict = {
            "name": opts.verbose_name,
            "obj": format_html('<a href="{}">{}</a>', current_path, self.object),
        }
        if "_save" in self.request.POST:
            message = _("The {name} “{obj}” was changed successfully.")
            success_url = reverse("accounts:home")
        else:
            message = _("The {name} “{obj}” was changed successfully. "
                        "You may edit it again below.")
            success_url = current_path
        messages.success(self.request, format_html(message, **msg_dict))
        return success_url

    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.has_read_perm():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.has_change_perm():
            messages.error(
                request, _("You don't have permission to edit this profile."))
            return redirect(
                reverse_lazy(
                    "accounts:profile", kwargs={"pk": self.request.user.pk.__str__()})
            )
        return super().post(request, *args, **kwargs)
