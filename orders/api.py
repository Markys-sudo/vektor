from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Order
from .permissions import IsOwner
from .serializers import OrderCreateSerializer, OrderSerializer

CANCELLABLE = (Order.Status.PENDING, Order.Status.PAID)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    ):

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == "create" else OrderSerializer

    def perform_destroy(self, instance):
        if instance.status not in CANCELLABLE:
            raise ValidationError("Нельзя отменить этот заказ.")
        instance.status = Order.Status.CANCELLED
        instance.save(update_fields=["status"])

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in CANCELLABLE:
            return Response(
                {"detail": "Нельзя отменить этот заказ."}, status=status.HTTP_400_BAD_REQUEST
            )
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)

