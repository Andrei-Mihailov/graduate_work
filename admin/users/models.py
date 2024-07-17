import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


class Group(models.Model):
    name = models.CharField(max_length=255,
                            unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "groups"  # "content\".\"groups"
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address',
                              max_length=255,
                              unique=True)
    username = models.CharField(max_length=255,
                                unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255,
                                  null=True)
    last_name = models.CharField(max_length=255,
                                 null=True)
    group = models.ForeignKey(Group,
                              default=None,
                              null=True,
                              on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'

    objects = MyUserManager()

    def __str__(self):
        return f'{self.email} {self.id}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = "user"  # "content\".\"user"
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
