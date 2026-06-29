from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class UpdateUserPasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]
        new_password_confirm = serializer.validated_data["new_password_confirm"]

        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Current password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != new_password_confirm:
            return Response(
                {
                    "new_password_confirm": [
                        "New password and confirmation do not match."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
        )


class RegisterView(
    mixins.CreateModelMixin, generics.GenericAPIView, mixins.UpdateModelMixin
):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        user = self.get_queryset().get(id=response.data["id"])
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": response.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class MeView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MeOrderView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders.all()
