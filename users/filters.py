import django_filters
from .models import Order
from django import forms



class OrderFilter(django_filters.FilterSet):

    date_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="Дата от"
    )

    date_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="Дата до"
    )

    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Order.Status.choices,
        label="Статус замовлення",
        empty_label="Всі статуси"
    )

    class Meta:
        model = Order
        fields = [
            "date_from",
            "date_to",
            "status",
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'status-select'}),       
        }