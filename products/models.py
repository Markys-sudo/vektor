"""Catalog models: categories and products."""

from django.db import models
from django.db.models import Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from .imaging import to_webp


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class ProductQuerySet(models.QuerySet):
    """Composable query logic — kept out of views/serializers."""

    def active(self) -> "ProductQuerySet":
        return self.filter(is_active=True)

    def with_rating(self) -> "ProductQuerySet":
        return self.annotate(
            # Если отзывов нет, вместо None запишется 0.0
            avg_rating=Coalesce(
                Avg("reviews__rating"), Value(0.0), output_field=models.FloatField()
            ),
            reviews_count=Count("reviews", distinct=True),
        )

    def with_popularity(self) -> "ProductQuerySet":
        return self.annotate(orders_count=Count("order_items", distinct=True))

    def in_category(self, slug: str) -> "ProductQuerySet":
        return self.filter(category__slug=slug)

    def search(self, term: str) -> "ProductQuerySet":
        return self.filter(Q(name__icontains=term) | Q(description__icontains=term))


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)

    objects = ProductQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(
                fields=["is_active", "category"], name="product_active_cat_idx"
            ),
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
        # Convert freshly-uploaded, non-WebP images to optimized WebP.
        # The .webp guard prevents re-processing on later saves (e.g. stock edits).
        # Product images are admin-uploaded (off the hot path), so doing this
        # synchronously is fine; for high-volume user uploads, offload to Celery.
        if self.image and not self.image.name.lower().endswith(".webp"):
            converted = to_webp(self.image)
            if converted is not None:
                name, content = converted
                self.image.save(name, content, save=False)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
