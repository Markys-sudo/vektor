from django.views.generic import DetailView
from django_filters.views import FilterView

from .filters import ProductFilter
from .models import Category, Product


class ProductListView(FilterView):
    model = Product
    filterset_class = ProductFilter
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return (
            Product.objects.active()
            .with_rating()
            .with_popularity()
            .select_related("category")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        ctx["categories"] = Category.objects.all()
        
        ctx["selected_categories"] = self.request.GET.getlist("category")
        return ctx


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
        # Local imports avoid any cross-app import cycle at module load.
        from reviews.forms import ReviewForm
        from reviews.services import has_purchased

        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["can_review"] = user.is_authenticated and has_purchased(user, self.object)
        ctx["review_form"] = ReviewForm()
        return ctx
