import logging
from http import HTTPStatus

from django.contrib import admin, messages
from notifications.models import Notification
from notifications.models import Template as TemplateModel

import sentry_sdk
from sentry_sdk import capture_message

logger = logging.getLogger(__name__)
sentry_sdk.init(
    dsn="https://7e322a912461958b85dcdf23716aeff5@o4507457845592064.ingest.de.sentry.io/4507457848016976"
)


class NotificationAdminUsersInline(admin.TabularInline):
    model = Notification.users.through
    extra = 0
    raw_id_fields = ("user",)
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"


class NotificationAdminGroupsInline(admin.TabularInline):
    model = Notification.groups.through
    extra = 0
    raw_id_fields = ("group",)
    verbose_name = "Группа"
    verbose_name_plural = "Группы"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    inlines = (NotificationAdminUsersInline, NotificationAdminGroupsInline)
    raw_id_fields = ("template",)
    actions = ("send_notification",)

    @admin.action(description="Отправить уведомление пользователям")
    def send_notification(self, request, queryset):
        for notification in queryset:
            logger.info(
                f"Отправка уведомления {notification} для пользователей {notification.recipients}"
            )
            capture_message(
                f"Отправка уведомления {notification} для пользователей {notification.recipients}",
                level="info",
            )
            status_code = notification.send()
            if status_code == HTTPStatus.OK:
                self.message_user(
                    request, f"{notification} успешно отправлено", messages.SUCCESS
                )
                capture_message(
                    f"Уведомление '{notification}' успешно отправлено.", level="info"
                )
            else:
                self.message_user(
                    request, f"Не удалось отправить {notification}", messages.ERROR
                )
                capture_message(
                    f"Ошибка при отправке уведомления: {notification}.", level="error"
                )


@admin.register(TemplateModel)
class TemplateAdmin(admin.ModelAdmin):
    pass
