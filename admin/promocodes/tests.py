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
            expiration_date=timezone.now() + timezone.timedelta(days=30),
        )

    def test_promo_code_creation(self):
        self.assertEqual(self.promo_code.code, "TEST2024")
        self.assertEqual(self.promo_code.discount, 10.0)
        self.assertEqual(
            self.promo_code.discount_type, PromoCode.DiscountType.PERCENTAGE
        )
        self.assertEqual(self.promo_code.num_uses, 5)
        self.assertTrue(self.promo_code.is_active)
        self.assertIsNotNone(self.promo_code.creation_date)
        self.assertIsNotNone(self.promo_code.expiration_date)

    def test_discount_type_choices(self):
        valid_choices = [choice[0] for choice in PromoCode.DiscountType.choices]
        self.assertIn(self.promo_code.discount_type, valid_choices)

    def test_num_uses(self):
        # Test default num_uses value
        promo_code = PromoCode.objects.create(code="TEST2025", discount=5.0)
        self.assertEqual(promo_code.num_uses, 1)

    def test_is_deleted(self):
        self.assertFalse(self.promo_code.is_deleted)
        self.promo_code.is_deleted = True
        self.promo_code.save()
        self.assertTrue(self.promo_code.is_deleted)

    def test_str_method(self):
        self.assertEqual(str(self.promo_code), "TEST2024")


class TariffModelTest(TestCase):

    def setUp(self):
        self.tariff = Tariff.objects.create(
            name="Basic Plan", price=29.99, description="A basic plan for users."
        )

    def test_tariff_creation(self):
        self.assertEqual(self.tariff.name, "Basic Plan")
        self.assertEqual(self.tariff.price, 29.99)
        self.assertEqual(self.tariff.description, "A basic plan for users.")

    def test_is_deleted_default(self):
        self.assertFalse(self.tariff.is_deleted)


class PurchaseModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.tariff = Tariff.objects.create(
            name="Basic Plan", price=29.99, description="A basic plan for users."
        )
        self.promo_code = PromoCode.objects.create(
            code="TEST2024",
            discount=10.0,
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            num_uses=5,
            is_active=True,
        )
        self.purchase = Purchase.objects.create(
            user=self.user,
            tariff=self.tariff,
            promo_code=self.promo_code,
            total_price=26.99,  # Price after discount
        )

    def test_purchase_creation(self):
        self.assertEqual(self.purchase.user, self.user)
        self.assertEqual(self.purchase.tariff, self.tariff)
        self.assertEqual(self.purchase.promo_code, self.promo_code)
        self.assertEqual(self.purchase.total_price, 26.99)
        self.assertIsNotNone(self.purchase.purchase_date)

    def test_default_purchase_date(self):
        self.assertEqual(self.purchase.purchase_date.date(), timezone.now().date())


class AvailableForUsersModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="testuser1")
        self.user2 = User.objects.create(username="testuser2")
        self.group1 = Group.objects.create(
            name="Test Group 1", description="A test group 1"
        )
        self.group2 = Group.objects.create(
            name="Test Group 2", description="A test group 2"
        )
        self.promo_code = PromoCode.objects.create(
            code="TEST2024",
            discount=10.0,
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            num_uses=5,
            is_active=True,
        )
        self.available = AvailableForUsers.objects.create(promo_code=self.promo_code)
        self.available.user.set([self.user1, self.user2])
        self.available.group.set([self.group1, self.group2])

    def test_available_for_users_creation(self):
        self.assertIn(self.user1, self.available.user.all())
        self.assertIn(self.user2, self.available.user.all())
        self.assertIn(self.group1, self.available.group.all())
        self.assertIn(self.group2, self.available.group.all())
        self.assertEqual(self.available.promo_code, self.promo_code)

    def test_add_users_to_available_for_users(self):
        new_user = User.objects.create(username="testuser3")
        self.available.user.add(new_user)
        self.assertIn(new_user, self.available.user.all())

    def test_add_groups_to_available_for_users(self):
        new_group = Group.objects.create(
            name="Test Group 3", description="A test group 3"
        )
        self.available.group.add(new_group)
        self.assertIn(new_group, self.available.group.all())

    def test_remove_user(self):
        self.available.user.remove(self.user1)
        self.assertNotIn(self.user1, self.available.user.all())

    def test_remove_group(self):
        self.available.group.remove(self.group1)
        self.assertNotIn(self.group1, self.available.group.all())

    def test_str_method(self):
        # To test str method, you might want to implement a __str__ method in the model
        self.assertEqual(str(self.available.promo_code), "TEST2024")
