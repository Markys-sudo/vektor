from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, OrderItem
from orders.services import create_order, CartLine
from orders.exceptions import OutOfStockError

User = get_user_model()


class OrderServicesTestCase(TestCase):
    def setUp(self):
        """Подготовка тестовых данных перед каждым тестом."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.category = Category.objects.create(name="Hops", slug="hops")

        # Создаем тестовый товар с запасом 10 штук
        self.product = Product.objects.create(
            name="Mosaic Hops",
            slug="mosaic-hops",
            price=Decimal("15.50"),
            category=self.category,
            stock=10,
            is_active=True,
        )

    def test_create_order_success(self):
        """Тест успешного создания заказа и списания остатков."""
        lines = [CartLine(product_id=self.product.id, quantity=3)]

        # Вызываем ваш сервис
        order = create_order(
            user=self.user, lines=lines, shipping_address="Test City, Test St. 1"
        )

        # Проверяем, что заказ создался корректно
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        # Проверяем расчет общей стоимости: 15.50 * 3 = 46.50
        self.assertEqual(order.total_price, Decimal("46.50"))

        # КРИТИЧНО: Проверяем, что остаток на складе уменьшился (10 - 3 = 7)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_create_order_out_of_stock(self):
        """Тест блокировки заказа, если товара недостаточно."""
        lines = [
            # Запрашиваем 11 штук при доступных 10
            CartLine(product_id=self.product.id, quantity=11)
        ]

        # Проверяем, что вызывается исключение OutOfStockError
        with self.assertRaises(OutOfStockError):
            create_order(
                user=self.user, lines=lines, shipping_address="Test City, Test St. 1"
            )

        # Проверяем, что заказ НЕ был создан в базе данных
        self.assertEqual(Order.objects.count(), 0)

        # Проверяем, что остаток товара остался нетронутым (ровно 10)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
