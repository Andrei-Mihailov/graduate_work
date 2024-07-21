from django.test import TestCase
from django.utils import timezone
from .models import PromoCode, Tariff, Purchase
from users.models import User, Group

class PromoCodeModelTest(TestCase):

    def setUp(self):
        self.promo_code = PromoCode.objects.create(
            code="SUMMER21",
            discount=20.0,
            is_active=True,
            creation_date=timezone.now().date()
        )

    def test_promo_code_creation(self):
        """Тестирование создания промокода"""
        promo_code = PromoCode.objects.get(code="SUMMER21")
        self.assertEqual(promo_code.discount, 20.0)
        self.assertTrue(promo_code.is_active)
        self.assertIsNotNone(promo_code.creation_date)

    def test_promo_code_str(self):
        """Тестирование метода __str__"""
        self.assertEqual(str(self.promo_code), "SUMMER21")

    def test_discount_validators(self):
        """Тестирование валидаторов для поля discount"""
        with self.assertRaises(ValueError):
            PromoCode.objects.create(code="WINTER21", discount=-10)
        with self.assertRaises(ValueError):
            PromoCode.objects.create(code="WINTER21", discount=110)


class TariffModelTest(TestCase):

    def setUp(self):
        self.tariff = Tariff.objects.create(
            name="Basic Plan",
            price=29.99,
            description="Basic plan with limited features."
        )

    def test_tariff_creation(self):
        """Тестирование создания тарифа"""
        tariff = Tariff.objects.get(name="Basic Plan")
        self.assertEqual(tariff.price, 29.99)
        self.assertEqual(tariff.description, "Basic plan with limited features.")

    def test_tariff_str(self):
        """Тестирование метода __str__"""
        self.assertEqual(str(self.tariff), "Basic Plan")


class PurchaseModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password"
        )
        self.tariff = Tariff.objects.create(
            name="Premium Plan",
            price=49.99,
            description="Premium plan with all features."
        )
        self.promo_code = PromoCode.objects.create(
            code="DISCOUNT50",
            discount=50.0,
            is_active=True,
            creation_date=timezone.now().date()
        )
        self.purchase = Purchase.objects.create(
            user=self.user,
            tariff=self.tariff,
            promo_code=self.promo_code,
            total_price=self.tariff.price * (1 - self.promo_code.discount / 100)
        )

    def test_purchase_creation(self):
        """Тестирование создания покупки"""
        purchase = Purchase.objects.get(user=self.user)
        self.assertEqual(purchase.tariff, self.tariff)
        self.assertEqual(purchase.promo_code, self.promo_code)
        self.assertEqual(purchase.total_price, self.tariff.price * (1 - self.promo_code.discount / 100))

    def test_purchase_date(self):
        """Тестирование поля purchase_date"""
        purchase = Purchase.objects.get(user=self.user)
        self.assertIsInstance(purchase.purchase_date, timezone.datetime)

    def test_purchase_str(self):
        self.assertEqual(str(self.purchase), f"Purchase of {self.tariff.name} by {self.user.username}")

class UserModelTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(
            name="Admin",
            description="Group with administrative privileges."
        )
        self.user = User.objects.create_user(
            username="testuser",
            group=self.group
        )

    def test_user_creation(self):
        """Тестирование создания пользователя"""
        user = User.objects.get(username="testuser")
        self.assertEqual(user.group, self.group)

    def test_user_str(self):
        """Тестирование метода __str__"""
        self.assertEqual(str(self.user), "testuser")

class GroupModelTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(
            name="Admin",
            description="Group with administrative privileges."
        )

    def test_group_creation(self):
        """Тестирование создания группы"""
        group = Group.objects.get(name="Admin")
        self.assertEqual(group.description, "Group with administrative privileges.")

    def test_group_str(self):
        """Тестирование метода __str__"""
        self.assertEqual(str(self.group), "Admin")