from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class TelegramConfirmAPIView(APIView):
    permission_classes = [] 

    def post(self, request):
        bot_secret = request.headers.get("X-Bot-Secret")
        if bot_secret != "SUPER_SECRET_TOKEN_FOR_MY_BOT":
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Бот присылает ID пользователя в поле 'auth_code'
        user_code = request.data.get("auth_code") 
        tg_id = request.data.get("telegram_id")
        tg_username = request.data.get("telegram_username")
        
        if not user_code or not tg_id:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # ИСПРАВЛЕНИЕ: принудительно переводим строку "4" в число 4
            user_id = int(user_code)
            
            # Ищем пользователя напрямую по ID
            user = User.objects.get(id=user_id)
            user.telegram_id = tg_id
            user.telegram_username = tg_username
            user.save()
            
            return Response({"status": "success", "username": user.username}, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError, User.DoesNotExist):
            # Если ID не число или такого пользователя нет в таблице User
            return Response({"error": "User not found or invalid ID"}, status=status.HTTP_400_BAD_REQUEST)


class TelegramLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Просто берем ID текущего пользователя из базы
        user_id = request.user.id
        
        bot_username = "tg_sh000p_bot"  # Имя вашего бота
        
        # Ссылка вида: https://t.me
        link = f"https://t.me/{bot_username}?start={user_id}"
        
        return Response({"link": link}, status=status.HTTP_200_OK)

