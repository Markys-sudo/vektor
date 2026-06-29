from django.urls import path

from .views import ProductDetailView, ProductListView
from django.views.generic import TemplateView

app_name = "products"

urlpatterns = [
    path("product", ProductListView.as_view(), name="product_list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path('guides-recipes/', 
        TemplateView.as_view(template_name="guides-recipes.html"), 
        name="guides_recipes"
    ),
    
]
