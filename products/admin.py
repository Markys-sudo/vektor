from django.contrib import admin
from django.db.models import Count

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "ordered_count")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "stock", "is_active")

    def get_queryset(self, request):
        # Annotation powers a sortable "ordered N times" column → top products.
        return super().get_queryset(request).annotate(_ordered=Count("order_items"))

    @admin.display(description="Заказан раз", ordering="_ordered")
    def ordered_count(self, obj):
        return obj._ordered
