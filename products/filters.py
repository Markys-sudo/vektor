"""Catalog filters (reused by both the web view and the REST API)."""
import django_filters

from .models import Category, Product

SORT_MAP = {
        "price": "price",
        "created_at": "-created_at",
        "orders_count": "-orders_count",
        "avg_rating": "-avg_rating",
}


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Пошук")
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label="Категорія")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Ціна від")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Ціна до")
    sort = django_filters.OrderingFilter(
        fields=(
            ("price", "price"),
            ("created_at", "created_at"),
            ("orders_count", "popular"),
            ("avg_rating", "rating"),
        ),
        field_labels={
            "price": "Цена",
            "created_at": "Новизна",
            "orders_count": "Популярность",
            "avg_rating": "Рейтинг",
        },
        label="Сортировка",
    )

    class Meta:
        model = Product
        fields = ["q", "category", "min_price", "max_price", "sort"]

    def filter_search(self, queryset, name, value):
        return queryset.search(value)
