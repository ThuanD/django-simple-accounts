import logging
from typing import Any, Dict, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

User = get_user_model()

DEFAULTS = {
    "SITE_TITLE": _("NOCOEM"),
    "SITE_HEADER": _("NOCOEM"),
    "LOGIN_URL": "/accounts/login/",
    "LOGIN_REDIRECT_URL": "/accounts/",
    "ADAPTER": "accounts.adapter.DefaultUserAdapter",
    "HOME_TEMPLATE": "accounts/home.html",
    "LOGIN_TEMPLATE": "accounts/login_form.html",
    "LOGOUT_TEMPLATE": "accounts/logged_out.html",
    "PROFILE_TEMPLATE": "accounts/profile_form.html",
    "PASSWORD_CHANGE_TEMPLATE": "accounts/password_change_form.html",
    "PASSWORD_CHANGE_DONE_TEMPLATE": "accounts/password_change_form.html",
    "PASSWORD_RESET_TEMPLATE": "accounts/password_reset_form.html",
    "PASSWORD_RESET_EMAIL_TEMPLATE": "accounts/password_reset_email.html",
    "PASSWORD_RESET_DONE_TEMPLATE": "accounts/password_reset_done.html",
    "PASSWORD_RESET_CONFIRM_TEMPLATE": "accounts/password_reset_confirm.html",
    "PASSWORD_RESET_COMPLETE_TEMPLATE": "accounts/password_reset_complete.html",
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = [
    "ADAPTER",
]


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (
            val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class Settings:
    def __init__(
            self,
            user_settings: Dict[str, Any] = None,
            defaults: Dict[str, Any] = None,
            import_strings: List[str] = None
    ):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            try:
                self._user_settings = getattr(settings, 'ACCOUNTS', {})
            except ImproperlyConfigured:
                raise AttributeError("Accounts setting not found")
        return self._user_settings

    def __getattr__(self, attr: str) -> Any:
        if attr not in self.defaults:
            raise AttributeError("Invalid ACCOUNTS setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self) -> None:
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


acc_settings = Settings(None, DEFAULTS, IMPORT_STRINGS)
settings.LOGIN_URL = acc_settings.LOGIN_URL
settings.LOGIN_REDIRECT_URL = acc_settings.LOGIN_REDIRECT_URL


def reload_acc_settings(*_: Any, **kwargs: Any) -> None:
    setting = kwargs["setting"]
    if setting == "ACCOUNTS":
        acc_settings.reload()
    settings.LOGIN_URL = acc_settings.LOGIN_URL
    settings.LOGIN_REDIRECT_URL = acc_settings.LOGIN_REDIRECT_URL


setting_changed.connect(reload_acc_settings)
