from rest_framework import serializers

from .exceptions import OutOfStockError
from products.models import Product
from .models import Order, OrderItem, CartItem
from .services import CartLine, create_order


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("product", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_price",
            "shipping_address",
            "items",
            "created_at",
        )


class OrderLineInputSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    items = OrderLineInputSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        lines = [
            CartLine(product_id=i["product"], quantity=i["quantity"])
            for i in validated_data["items"]
        ]
        try:
            return create_order(
                user=user,
                lines=lines,
                shipping_address=validated_data["shipping_address"],
            )
        except OutOfStockError as exc:
            raise serializers.ValidationError({"items": str(exc)})

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class ProductMinSerializer(serializers.ModelSerializer):
    """Спрощений серіалізатор товару для відображення всередині кошика."""

    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "image"]


class CartItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для відображення елемента кошика."""

    product = ProductMinSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class UpdateCartItemSerializer(serializers.Serializer):
    """Серіалізатор для додавання/оновлення кількості товару."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    replace = serializers.BooleanField(default=False)

    def validate_product_id(self, value):
        if not Product.objects.filter(
            id=value, is_active=True
        ).exists():  # або .active() замість filter
            raise serializers.ValidationError("Product not found or inactive.")
        return value
