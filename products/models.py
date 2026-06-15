from django.db import models
from django.db.models import Avg, Count, Q

from .imaging import to_webp

class TimeStampedModel(models.Model):
    """Abstract base class that provides self-updating 'created_at' and 'updated_at' fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
class ProductQuerySet(models.QuerySet):
    
    def active(self)->"ProductQuerySet":
        return self.filter(is_active=True)
    
    def with_rating(self)->"ProductQuerySet":
        return self.annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews",distinct=True),
        )
    
    def with_popularity(self)->"ProductQuerySet":
        return self.annotate(
            orders_count=Count("order_items",distinct=True)
        )
        
    def in_category(self, slug:str)->"ProductQuerySet":
        return self.filter(category__slug=slug)
    
    def search(self, query:str)->"ProductQuerySet":
        return self.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        
class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    image = models.ImageField(upload_to="products/images/", blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)

    objects = ProductQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "category"], name="product_active_cat_idx"),
            models.Index(fields=["price"], name="product_price_idx"),
            models.Index(fields=["-created_at"], name="product_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="product_price_non_negative"
                ),
            models.CheckConstraint(
                condition=models.Q(stock__gte=0), name="product_stock_non_negative"
                ),
        ]
    def save(self, *args, **kwargs):
        if self.image and not self.image.name.endswith(".webp"):
            result = to_webp(self.image)
            if result is not None:
                filename, content_file = result
                self.image.save(filename, content_file, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name