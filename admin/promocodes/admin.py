import random
import string

from django.contrib import admin, messages
from django.contrib.auth.models import User, Group

from . import models

admin.site.unregister(User)
admin.site.unregister(Group)


class PurchaseInline(admin.TabularInline):
    model = models.Purchase

    readonly_fields = (
        'user',
        'tariff',
        'total_price',
        'purchase_date'
    )
    extra = 0
    show_change_link = True
    verbose_name = "Покупка"
    verbose_name_plural = "Покупки"

    def has_add_permission(self, request, *kwargs):
        return False


class PromoCode(admin.ModelAdmin):
    fields = [
        'code',
        ('discount', 'discount_type'),
        ('num_uses', 'expiration_date'),
        ('is_active', 'creation_date'),
    ]
    list_display = (
        'code',
        'discount',
        'discount_type',
        'num_uses',
        'expiration_date',
        'is_active'
    )
    search_fields = (
        'code',
        'discount',
        'num_uses',
        'discount_type'
    )
    ordering = (
        'discount_type',
        'num_uses',
        'expiration_date',
        'is_active')
    readonly_fields = (
        'creation_date',

    )
    exclude = ('is_deleted',)
    inlines = [PurchaseInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'code':
            kwargs['initial'] = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.action(description='Удалить')
    def delete_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_deleted = True
                obj.save()
            self.message_user(request,
                              f"{len(queryset)} промокод(ов) удалено",
                              messages.SUCCESS)
        except Exception:
            self.message_user(request, "Что-то пошло не так, попробуйте снова.", messages.ERROR)

    actions = [delete_selected]


class Tariff(admin.ModelAdmin):
    fields = [
        ('name', 'price'),
        'description'
    ]
    list_display = (
        'name',
        'price'
    )
    search_fields = [
        'name',
        'description'
    ]
    exclude = ('is_deleted',)

    @admin.action(description='Удалить')
    def delete_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_deleted = True
                obj.save()
            self.message_user(request,
                              f"{len(queryset)} промокод(ов) удалено",
                              messages.SUCCESS)
        except Exception:
            self.message_user(request, "Что-то пошло не так, попробуйте снова.", messages.ERROR)

    actions = [delete_selected]


class Purchase(admin.ModelAdmin):
    fields = [
        'user',
        ('tariff', 'promo_code'),
        ('total_price', 'purchase_date')
    ]
    list_display = (
        'user',
        'tariff',
        'promo_code',
        'total_price',
        'purchase_date'
    )
    search_fields = [
        'user',
        'tariff',
        'promo_code'
    ]
    ordering = ('purchase_date',)
    readonly_fields = (
        'user',
        'tariff',
        'promo_code',
        'total_price',
        'purchase_date'
    )
    exclude = ('image_url',)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.PromoCode, PromoCode)
admin.site.register(models.Tariff, Tariff)
admin.site.register(models.Purchase, Purchase)
