import json

from django.db import models
from django.core.cache import cache


class PromoCode(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed"
        PERCENTAGE = "percentage"
        TRIAL = "trial"

    code = models.CharField(verbose_name="Промокод", max_length=255, unique=True)
    discount = models.FloatField(verbose_name="Размер скидки", default=0)
    discount_type = models.CharField(
        verbose_name="Тип скидки",
        max_length=15,
        choices=DiscountType.choices,
        default=DiscountType.FIXED,
    )
    num_uses = models.PositiveIntegerField(
        verbose_name="Доступное количество использований", default=1
    )
    is_active = models.BooleanField(verbose_name="Действителен", default=True)
    creation_date = models.DateField(verbose_name="Дата создания", auto_now_add=True)
    expiration_date = models.DateField(
        verbose_name="Срок действия", default=None, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if self.is_deleted or not self.is_active:
            cache.delete(self.code)
        else:
            cache.set(self.code, 1)
        return super(PromoCode, self).save(*args, **kwargs)

    class Meta:
        db_table = "promo_codes"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"


class Tariff(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    price = models.FloatField(verbose_name="Стоимость")
    description = models.CharField(verbose_name="Описание", max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tariffs"
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"


class Purchase(models.Model):
    user = models.ForeignKey(
        "users.User", verbose_name="Пользователь", on_delete=models.DO_NOTHING
    )
    tariff = models.ForeignKey(
        Tariff, verbose_name="Тариф", on_delete=models.DO_NOTHING
    )
    promo_code = models.ForeignKey(PromoCode, on_delete=models.DO_NOTHING)
    total_price = models.FloatField(verbose_name="Итоговая стоимость")
    purchase_date = models.DateField(verbose_name="Дата покупки", auto_now_add=True)

    def __str__(self):
        return f"{self.tariff} - {self.purchase_date}"

    class Meta:
        db_table = "purchases"
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"


class AvailableForUsers(models.Model):
    user = models.ManyToManyField("users.User", verbose_name="Пользователь", blank=True)
    group = models.ManyToManyField(
        "users.Group", verbose_name="Группа пользователей", blank=True
    )
    promo_code = models.ForeignKey(
        PromoCode, verbose_name="Промокод", on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.promo_code.code

    class Meta:
        db_table = "availables"
        verbose_name = "Доступ"
        verbose_name_plural = "Доступы"
