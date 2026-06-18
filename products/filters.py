"""Catalog filters (reused by both the web view and the REST API)."""
import django_filters

from .models import Category, Product


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Поиск")
    
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        field_name="category",
        label="Категория",
        to_field_name="slug",
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Цена от")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Цена до")
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
