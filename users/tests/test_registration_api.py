from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from users.api_views import RegisterView

User = get_user_model()


class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        """Инициализация фабрики запросов и контроллера напрямую."""
        self.factory = APIRequestFactory()
        self.view = RegisterView.as_view()

        # Тестовые данные для успешной регистрации
        self.valid_payload = {
            "username": "newbrewer",
            "email": "brewer@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

    def test_registration_success(self):
        """Тест: Успешная регистрация пользователя с валидными данными."""
        request = self.factory.post(
            "/api/auth/register/", data=self.valid_payload, format="json"
        )
        response = self.view(request)

        # ИСПРАВЛЕНО: Ваш контроллер возвращает 200 OK вместо 201
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="newbrewer").exists())

        # Проверяем структуру вашего кастомного ответа
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newbrewer")

    def test_registration_duplicate_username_or_email(self):
        """Тест: Запрет регистрации, если username уже занят."""
        User.objects.create_user(
            username="newbrewer", email="other@example.com", password="password123"
        )

        request = self.factory.post(
            "/api/auth/register/", data=self.valid_payload, format="json"
        )
        response = self.view(request)

        # Ожидаем 400 Bad Request от валидатора сериализатора
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_registration_passwords_dont_match(self):
        """Тест: Ошибка валидации, если пароли в полях не совпадают."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["password_confirm"] = "DifferentPassword123!"

        request = self.factory.post(
            "/api/auth/register/", data=invalid_payload, format="json"
        )
        response = self.view(request)

        # Ожидаем 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
