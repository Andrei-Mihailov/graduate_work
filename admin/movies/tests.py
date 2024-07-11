from django.test import TestCase
from .models import PromoCode


class PromoCodeModelTest(TestCase):
    def test_create_promocode(self):
        promo = PromoCode.objects.create(code="TESTCODE", discount=10)
        self.assertEqual(promo.code, "TESTCODE")
        self.assertEqual(promo.discount, 10)
