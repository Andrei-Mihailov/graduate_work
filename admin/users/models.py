from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Group(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255, unique=True)
    description = models.CharField(verbose_name="Описание", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "groups"
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    group = models.ManyToManyField(Group, verbose_name="Группы", blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
