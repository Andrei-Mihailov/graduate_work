from django.db import models


class StatusChoice(models.TextChoices):
    SENT = "sent", "Отправлено"
    PENDING = "pending", "В процессе"
    FAILED = "failed", "Не отправлено"


class NotificationTypeChoice(models.TextChoices):
    PERSONAL = "personal", "Индивидуальная"
    GROUP = "group", "Групповая"
