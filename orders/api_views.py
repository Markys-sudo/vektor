from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from products.models import Product
from .cart import Cart
from .serializers import CartItemSerializer, UpdateCartItemSerializer


class CartViewSet(viewsets.GenericViewSet):
    """
    Керування кошиком поточного користувача.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Вказуємо DRF (та Swagger), які серіалізатори використовуються
        для різних дій (actions).
        """
        if self.action == "create":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def list(self, request):
        """Отримати вміст кошика, загальну вартість та кількість товарів."""
        cart = Cart(request.user)
        # Використовуємо self.get_serializer замість прямого виклику класу
        serializer = self.get_serializer(cart.items(), many=True)
        return Response(
            {
                "items": serializer.data,
                "total_count": cart.count(),
                "total_price": str(cart.total_price()),
            }
        )

    def create(self, request):
        """Додати товар до кошика або змінити його кількість."""
        # Тепер self.get_serializer автоматично візьме UpdateCartItemSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
        cart = Cart(request.user)

        item = cart.add_to_cart(
            product,
            quantity=serializer.validated_data["quantity"],
            replace=serializer.validated_data["replace"],
        )

        if item is None:
            return Response(
                {"detail": "Item removed from cart."}, status=status.HTTP_200_OK
            )
        return Response(
            CartItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """Повністю очистити кошик."""
        cart = Cart(request.user)
        cart.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"], url_path="remove/(?P<product_id>[0-9]+)")
    def remove_item(self, request, product_id=None):
        """Видалити один конкретний товар з кошика."""
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request.user)
        cart.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
