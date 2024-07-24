import uuid

from django.test import TestCase
from django.utils import timezone

from .models import PromoCode, Tariff, Purchase, AvailableForUsers
from users.models import User, Group


class PromoCodeModelTest(TestCase):

    def setUp(self):
        self.promo_code = PromoCode.objects.create(
            code="TEST2024",
            discount=10.0,
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            num_uses=5,
            is_active=True,
            expiration_date=timezone.now() + timezone.timedelta(days=30)
        )

    def test_promo_code_creation(self):
        self.assertEqual(self.promo_code.code, "TEST2024")
        self.assertEqual(self.promo_code.discount, 10.0)
        self.assertEqual(self.promo_code.discount_type, PromoCode.DiscountType.PERCENTAGE)
        self.assertEqual(self.promo_code.num_uses, 5)
        self.assertTrue(self.promo_code.is_active)
        self.assertIsNotNone(self.promo_code.creation_date)
        self.assertIsNotNone(self.promo_code.expiration_date)

    def test_str_method(self):
        self.assertEqual(str(self.promo_code), "TEST2024")

    def test_promo_code_delete(self):
        self.assertFalse(self.promo_code.is_deleted)
        self.promo_code.is_deleted = True
        self.assertTrue(self.promo_code.is_deleted)


class TariffModelTest(TestCase):

    def setUp(self):
        self.tariff = Tariff.objects.create(
            name="Basic Plan",
            price=29.99,
            description="A basic plan for users."
        )

    def test_tariff_creation(self):
        self.assertEqual(self.tariff.name, "Basic Plan")
        self.assertEqual(self.tariff.price, 29.99)
        self.assertEqual(self.tariff.description, "A basic plan for users.")

    def test_is_deleted_default(self):
        self.assertFalse(self.tariff.is_deleted)
        self.tariff.is_deleted = True
        self.assertTrue(self.tariff.is_deleted)


class PurchaseModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(uuid=uuid.uuid4(),
                                        email="testuser@example.com")
        self.tariff = Tariff.objects.create(
            name="Basic Plan",
            price=29.99,
            description="A basic plan for users."
        )
        self.promo_code = PromoCode.objects.create(
            code="TEST2024",
            discount=10.0,
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            num_uses=5,
            is_active=True
        )
        self.purchase = Purchase.objects.create(
            user=self.user,
            tariff=self.tariff,
            promo_code=self.promo_code,
            total_price=26.99  # Price after discount
        )

    def test_purchase_creation(self):
        self.assertEqual(self.purchase.user, self.user)
        self.assertEqual(self.purchase.tariff, self.tariff)
        self.assertEqual(self.purchase.promo_code, self.promo_code)
        self.assertEqual(self.purchase.total_price, 26.99)
        self.assertIsNotNone(self.purchase.purchase_date)


class AvailableForUsersModelTest(TestCase):

    def setUp(self):
        self.user = self.user = User.objects.create(uuid=uuid.uuid4(),
                                                    email="testuser@example.com")
        self.group = Group.objects.create(name="Test Group", description="A test group")
        self.promo_code = PromoCode.objects.create(
            code="TEST2024",
            discount=10.0,
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            num_uses=5,
            is_active=True
        )
        self.available = AvailableForUsers.objects.create(promo_code=self.promo_code)
        self.available.user.set([self.user])
        self.available.group.set([self.group])

    def test_available_for_users_creation(self):
        self.assertIn(self.user, self.available.user.all())
        self.assertIn(self.group, self.available.group.all())
        self.assertEqual(self.available.promo_code, self.promo_code)

    def test_str_method(self):
        self.assertEqual(str(self.available.promo_code), "TEST2024")
