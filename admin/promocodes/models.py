from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PromoCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    discount = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    creation_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "promo_codes"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"


class Tariff(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "tariffs"
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"


class Purchase(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING)
    tariff = models.ForeignKey(Tariff, on_delete=models.DO_NOTHING)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.DO_NOTHING)
    total_price = models.FloatField()
    purchase_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "purchases"
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
