from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PromocodesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "promocodes"
    verbose_name = _("promocodes")
