import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "groups"
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(Group, default=None, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
