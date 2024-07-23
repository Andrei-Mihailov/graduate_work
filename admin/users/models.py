import uuid

from django.db import models


class Group(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=255,
        unique=True)
    description = models.CharField(
        verbose_name="Описание",
        max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "groups"
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class User(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField(
        primary_key=True,
        null=False,
        max_length=255,
        unique=True)
    group = models.ManyToManyField(
        Group,
        verbose_name="Группы",
        blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    # def save()

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
