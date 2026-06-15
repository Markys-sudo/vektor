from django.views.generic import DetailView
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet
from.serializers import ProductSerializer

from .filters import ProductFilter
from .models import Product, Category

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.active().with_rating().with_popularity()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter


class ProductListView(FilterView):
    model = Product
    filterset_class = ProductFilter
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12
    
    def get_queryset(self):
        return (
            Product.objects.active()
            .with_rating()
            .with_popularity()
            .select_related("category")
            .order_by("-created_at")
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context
    
class ProductDetailView(DetailView):
    template_name = "products/product_detail.html"
    context_object_name = "product"
    
    def get_queryset(self):
        return (
            Product.objects.active()
            .with_rating()
            .select_related("category")
            .prefetch_related("reviews__user")
        )               
        
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        
        pass #MARK: Add related products, reviews, etc. to context if needed
    
        return context
