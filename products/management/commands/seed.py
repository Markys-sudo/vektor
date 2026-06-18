"""Populate the catalog with the Hop & Barley demo products (with images)."""
import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Category, Product

CATEGORIES = [("Hops", "hops"), ("Malts", "malts"), ("Yeast", "yeast"), ("Adjuncts", "adjuncts")]


PRODUCTS = [
    ("Citra Hops", "citra-hops", "hops", "citra_hops.jpg",
     "5.99", "Ideal for IPAs and Pale Ales"),
    ("Maris Otter Pale Malt", "maris-otter-malt", "malts", "maris_otter_malt.jpg",
     "2.50", "Perfect for traditional ales"),
    ("SafAle US-05 Dry Ale Yeast", "safale-us05-yeast", "yeast", "safale_us05_yeast.jpg",
     "3.25", "Clean fermenting American ale yeast"),
    ("Cascade Hops", "cascade-hops", "hops", "cascade_hops.jpg",
     "7.49", "Great for dry hopping"),
    ("Caramel Malt 60L", "caramel-malt", "malts", "caramel_malt.jpg",
     "3.00", "Head retention in darker beers"),
    ("Saaz Hops", "saaz-hops", "hops", "saaz_hops.jpg",
     "4.75", "Essential for Lagers"),
    ("Pilsner Malt", "pilsner-malt", "malts", "pilsner_malt.jpg",
     "2.20", "Foundation for lagers and pilsners"),
    ("Imperial Organic Yeast A07", "imperial-yeast", "yeast", "imperial_yeast.jpg",
     "8.99", "American ales with citrus notes"),
    ("Centennial Hops", "centennial-hops", "hops", "centennial_hops.jpg",
     "6.20", "Often called Super Cascade"),
    ("Mosaic Hops", "mosaic-hops", "hops", "mosaic_hops.jpg",
     "9.50", "Ideal for IPAs and Pale Ales"),
    ("West Coast IPA - All-Grain Kit", "west-coast-ipa-kit", "adjuncts", "ipa_kit.jpg",
     "60.00", "Complete West Coast IPA kit"),
    ("Unmalted Wheat", "unmalted-wheat", "adjuncts", "unmalted_wheat.jpg",
     "1.80", "For Belgian Witbier"),
]


class Command(BaseCommand):
    help = "Создаёт демо-товары Hop & Barley (с картинками)."

    def handle(self, *args, **options):
        cats = {}
        for name, slug in CATEGORIES:
            cats[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})

        img_dir = Path(settings.BASE_DIR) / "static" / "img" / "products"
        created = 0
        for name, slug, cat_slug, img, price, desc in PRODUCTS:
            product, made = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": cats[cat_slug],
                    "price": Decimal(price),
                    "stock": random.randint(8, 60),
                    "description": desc,
                },
            )
            created += int(made)
            if not product.image:
                path = img_dir / img
                if path.exists():
                    with path.open("rb") as fh:
                        product.image.save(img, File(fh), save=True)  # save() -> WebP
        self.stdout.write(self.style.SUCCESS(f"Готово. Новых товаров: {created}."))
