from django.contrib.admin.helpers import ActionForm
from django import forms

from promocodes.models import PromoCode, Tariff


class XForm(ActionForm):
    promo_code = forms.ModelChoiceField(
        queryset=PromoCode.objects.filter(is_active=True, is_deleted=False),
        label='Промокод:',
        required=False,
        empty_label="Выберите промокод"
    )
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.filter(is_deleted=False),
        label='Тариф:',
        required=False,
        empty_label="Выберите тариф"
    )

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
