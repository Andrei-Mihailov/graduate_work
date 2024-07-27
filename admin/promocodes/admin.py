import random
import string
import datetime
import sentry_sdk

from django.contrib import admin, messages
from django.contrib.auth.models import User, Group

from . import models

admin.site.unregister(User)
admin.site.unregister(Group)


class PurchaseInline(admin.TabularInline):
    model = models.Purchase

    readonly_fields = ("user", "tariff", "total_price", "purchase_date")
    extra = 0
    show_change_link = True
    verbose_name = "Покупка"
    verbose_name_plural = "Покупки"

    def has_add_permission(self, request, *kwargs):
        return False


class AvailablesInline(admin.TabularInline):
    model = models.AvailableForUsers

    fields = ["promo_code", ("user", "group")]
    list_display = ("promo_code", "get_users", "get_groups")
    extra = 1
    show_change_link = True
    verbose_name = "Доступ"
    verbose_name_plural = "Доступы"

    def get_users(self, obj):
        return ", ".join([str(user) for user in obj.user.filter(is_active=True)])
    get_users.short_description = "Пользователи"


class PromoCode(admin.ModelAdmin):
    fields = [
        "code",
        ("discount", "discount_type"),
        ("num_uses", "expiration_date"),
        ("is_active", "creation_date"),
    ]
    list_display = (
        "code",
        "discount",
        "discount_type",
        "num_uses",
        "get_purchase",
        "expiration_date",
        "is_active",
    )
    search_fields = ("code", "discount", "num_uses", "discount_type")
    list_filter = ("discount_type", "num_uses", "expiration_date", "is_active")
    readonly_fields = ("creation_date",)
    exclude = ("is_deleted",)
    inlines = [PurchaseInline, AvailablesInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "code":
            kwargs["initial"] = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(is_deleted=False,  # Только не удаленные промокоды
                       expiration_date__gte=datetime.datetime.now(),  # подходящие по сроку действия
                       num_uses__gte=0)  # доступные для использования
        return qs

    def get_purchase(self, obj):
        return models.Purchase.objects.filter(promo_code=obj).count()
    get_purchase.short_description = "Использован, раз"

    @admin.action(description="Удалить")
    def delete_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_deleted = True
                obj.save()
            self.message_user(
                request, f"{len(queryset)} промокод(ов) удалено", messages.SUCCESS
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.message_user(
                request, "Что-то пошло не так, попробуйте снова.", messages.ERROR
            )

    @admin.action(description="Деактивировать")
    def deactivate_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_active = False
                obj.save()
            self.message_user(
                request,
                f"{len(queryset)} промокод(ов) деактивировано",
                messages.SUCCESS,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.message_user(
                request, "Что-то пошло не так, попробуйте снова.", messages.ERROR
            )

    actions = [delete_selected, deactivate_selected]


class Tariff(admin.ModelAdmin):
    fields = [("name", "price"), "description"]
    list_display = ("name", "price", "description")
    search_fields = ("name", "description")
    exclude = ("is_deleted",)

    @admin.action(description="Удалить")
    def delete_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_deleted = True
                obj.save()
            self.message_user(
                request, f"{len(queryset)} тариф(ов) удалено", messages.SUCCESS
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.message_user(
                request, "Что-то пошло не так, попробуйте снова.", messages.ERROR
            )

    actions = [delete_selected]


class Purchase(admin.ModelAdmin):
    fields = ["user", ("tariff", "promo_code"), ("total_price", "purchase_date")]
    list_display = ("user", "tariff", "promo_code", "total_price", "purchase_date")
    search_fields = ("user", "tariff", "promo_code")
    list_filter = ("purchase_date",)
    readonly_fields = ("user", "tariff", "promo_code", "total_price", "purchase_date")

    def has_add_permission(self, request, obj=None):
        return False


class AvailableForUsers(admin.ModelAdmin):
    fields = ["promo_code", ("user", "group")]
    list_display = ("promo_code", "get_users", "get_groups")
    search_fields = ("promo_code",)

    def get_users(self, obj):
        return ", ".join([str(user) for user in obj.user.filter(is_active=True)])
    get_users.short_description = "Пользователи"

    def get_groups(self, obj):
        return ", ".join([str(group) for group in obj.group.all()])
    get_groups.short_description = "Группы пользователей"


admin.site.register(models.PromoCode, PromoCode)
admin.site.register(models.Tariff, Tariff)
admin.site.register(models.Purchase, Purchase)
admin.site.register(models.AvailableForUsers, AvailableForUsers)
