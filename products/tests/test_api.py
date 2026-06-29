from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from reviews.models import Review

User = get_user_model()


class ProductAPITestCase(APITestCase):
    def setUp(self):
        """Подготовка данных для API: категории, товары и отзывы."""
        self.category = Category.objects.create(name="Malt", slug="malt")

        # Товар 1: Высокий рейтинг (5.0)
        self.product_high = Product.objects.create(
            name="Caramel Malt 60L",
            slug="caramel-malt-60l",
            price=Decimal("3.00"),
            category=self.category,
            stock=50,
            is_active=True,
        )
        # Товар 2: Ниже рейтинг (3.0)
        self.product_low = Product.objects.create(
            name="Base Pale Ale Malt",
            slug="base-pale-ale-malt",
            price=Decimal("2.50"),
            category=self.category,
            stock=100,
            is_active=True,
        )

        # Создаем тестовых пользователей для отзывов
        self.user1 = User.objects.create_user(username="u1", password="p1")
        self.user2 = User.objects.create_user(username="u2", password="p2")

        # Добавляем отзывы (Товар 1 получает 5, Товар 2 получает 3)
        Review.objects.create(
            user=self.user1, product=self.product_high, rating=5, comment="Great!"
        )
        Review.objects.create(
            user=self.user2, product=self.product_low, rating=3, comment="Normal"
        )

        # URL для эндпоинта списка продуктов (измените имя роута, если в API оно другое)
        self.list_url = reverse("products-list")

    def test_get_product_list_api(self):
        """Тест: Успешный GET запрос списка товаров и проверка полей рейтинга."""
        response = self.client.get(self.list_url)

        # Проверяем HTTP статус 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Если у вас настроена пагинация DRF, данные будут в ['results']
        data = response.data.get("results", response.data)

        # Проверяем, что вернулось ровно 2 товара
        self.assertEqual(len(data), 2)

        # Проверяем, что сериализатор отдает поле avg_rating (если оно добавлено в Serializer)
        # Если вы еще не добавляли его в сериализатор, тест укажет на это
        first_product = data[0]
        self.assertIn("avg_rating", first_product)

    def test_api_sorting_by_rating(self):
        """Тест: Сортировка через API (?sort=rating) поднимает топ-рейтинг наверх."""
        response = self.client.get(self.list_url, {"sort": "rating"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)

        # Первым в списке должен идти товар с самым высоким рейтингом
        self.assertEqual(data[0]["slug"], "caramel-malt-60l")
        self.assertEqual(data[1]["slug"], "base-pale-ale-malt")
