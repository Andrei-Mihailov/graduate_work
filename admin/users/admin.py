import random
import string
import sentry_sdk

from django.contrib import admin, messages
from django.db.models import Count, Q, F

from promocodes.models import PromoCode, Purchase, AvailableForUsers
from . import models
from .forms import XForm


# генерация тестовых данных
# for i in range(5):
#     models.Group.objects.create(name="".join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

# domain = "example.com"
# for i in range(100):
#     username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
#     user = models.User.objects.create(email=f"{username}@{domain}")
#     for k in range(random.randint(1, 5)):
#         group = models.Group.objects.get(id=random.randint(1, 5))
#         user.group.add(group)


class Group(admin.ModelAdmin):
    list_display = ("name", "description")


class User(admin.ModelAdmin):
    fields = (
        "email",
        "group"
    )
    list_display = (
        "email",
        "get_group",
        "get_purchases",
        "get_availables"
    )
    readonly_fields = ("email",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(is_active=True)  # Только активные пользователи
        return qs

    def get_group(self, obj: models.User):
        return ", ".join([str(group) for group in obj.group.all()])
    get_group.short_description = "Группы"

    def get_purchases(self, obj):
        return Purchase.objects.filter(user=obj).count()
    get_purchases.short_description = "Количество использованных промокодов"

    def get_availables(self, obj: models.User):
        total_count = AvailableForUsers.objects.filter(
            Q(user=obj) | Q(group__in=obj.group.all())
        ).values('promo_code').annotate(count=Count('promo_code')).count()

        return total_count
    get_availables.short_description = "Количество доступных промокодов"

    @admin.action(description="Применить промокод")
    def apply_promocode_selected(self, request, queryset):
        try:
            promo_code_id = request.POST.get('promo_code')
            promo_code = PromoCode.objects.get(id=promo_code_id)
            tariff_id = request.POST.get('tariff')
            count_users = 0
            for obj in queryset:
                if promo_code.num_uses > 0:
                    promo_code.num_uses += 1
                    promo_code.save()
                    # PromoCode.objects.filter(id=promo_code_id).update(num_uses=F('num_uses') - 1)
                    if not AvailableForUsers.objects.filter(
                        Q(user=obj, promo_code=promo_code) |
                        Q(group__in=obj.group.all(), promo_code=promo_code)
                    ).values('promo_code').annotate(count=Count('promo_code')).count():
                        avu, _ = AvailableForUsers.objects.get_or_create(promo_code=promo_code)
                        avu.user.add(obj)
                    count_users += 1
                    sentry_sdk.capture_message(f'Применен промокод: {promo_code.code}. Пользователь - {obj.email}')
                    mess = f"/apply_promocode?promocode_id={promo_code_id}&tariff={tariff_id}"
                    type_mess = messages.SUCCESS
                else:
                    if count_users:
                        mess = f"/apply_promocode?promocode_id={promo_code_id}&tariff={tariff_id} -----> Применено промокодов: {count_users}"

                        type_mess = messages.WARNING
                    else:
                        mess = "Количество допустимых применений промокода равно 0"
                        type_mess = messages.ERROR
                    break
            self.message_user(request, mess, type_mess)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.message_user(
                request, "Что-то пошло не так, попробуйте снова", messages.ERROR
            )

    @admin.action(description="Удалить")
    def delete_selected(self, request, queryset):
        try:
            for obj in queryset:
                obj.is_active = False
                obj.save()
            self.message_user(
                request, f"{len(queryset)} пользователь(ей) удалено", messages.SUCCESS
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.message_user(
                request, "Что-то пошло не так, попробуйте снова.", messages.ERROR
            )

    action_form = XForm
    actions = [delete_selected, apply_promocode_selected]

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.User, User)
admin.site.register(models.Group, Group)
