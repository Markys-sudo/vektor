from django.contrib import admin
from django.db.models import Sum

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "shipping_address")
    inlines = [OrderItemInline]
    actions = ["mark_paid", "mark_shipped"]

    @admin.action(description="Отметить оплаченными")
    def mark_paid(self, request, queryset):
        queryset.update(status=Order.Status.PAID)

    @admin.action(description="Отметить отправленными")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        paid = Order.objects.filter(status=Order.Status.PAID)
        extra_context["revenue"] = paid.aggregate(total=Sum("total_price"))["total"] or 0
        extra_context["orders_total"] = Order.objects.count()
        return super().changelist_view(request, extra_context=extra_context)
