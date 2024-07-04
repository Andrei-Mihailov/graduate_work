import json
import logging
from typing import Annotated, List

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from notifications.enums import NotificationTypeChoice, StatusChoice

User = get_user_model()


logger = logging.getLogger(__name__)


class Template(models.Model):
    slug = models.SlugField("slug шаблона", max_length=50, primary_key=True)
    title = models.CharField("Заголовок", max_length=250)
    description = models.CharField("Описание шаблона", max_length=250)
    content = models.TextField(
        "Контент шаблона",
        help_text="Текст шаблона письма - HTML страница или просто текст.",
    )

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"

    def __str__(self):
        return f"Шаблон: {self.title}"


class Notification(models.Model):
    template = models.ForeignKey("Template", on_delete=models.CASCADE)
    name = models.CharField("Название", max_length=50)
    type = models.CharField(
        "Тип рассылки",
        max_length=50,
        choices=NotificationTypeChoice.choices,
        default=NotificationTypeChoice.GROUP,
    )
    users = models.ManyToManyField(
        User, related_name="notifications", through="NotificationToUser"
    )
    groups = models.ManyToManyField(
        Group, related_name="notifications", through="NotificationToGroup"
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"Уведомление: {self.name}"

    @property
    def recipients(self) -> User | List[User]:
        groups = self.groups.all()
        groups_users = []
        for group in groups:
            groups_users.extend([user for user in group.user_set.all()])
        return list(self.users.all()) + groups_users

    @property
    def recipients_ids(self) -> List[Annotated[str, "User's ids"]]:
        return [str(user.id) for user in self.recipients]

    def send(self) -> Annotated[int, "Status code"]:
        ids = (
            self.recipients_ids
            if self.type == NotificationTypeChoice.GROUP
            else self.recipients_ids[0]
        )
        usernames = [user.get_full_name() for user in self.recipients]
        context = {
            "title": self.template.title,
            "text": self.template.content,
            "username": usernames
            if self.type == NotificationTypeChoice.GROUP
            else usernames[0],
        }
        url = settings.EVENT_URL

        payload = {
            "receiver": ids,
            "event_name": self.template.slug,
            "event_type": self.name,
            "context": context,
            "type": self.type,
        }

        response = requests.post(url, json=payload)
        return response.status_code


class NotificationToUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)

    retry_count = models.IntegerField(verbose_name="Повторных попыток", default=0)
    status = models.CharField(
        verbose_name="Статус",
        max_length=10,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
    )
    last_update = models.DateTimeField(
        verbose_name="Последнее обновление", auto_now=True
    )


class NotificationToGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
