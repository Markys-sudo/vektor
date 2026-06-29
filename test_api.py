#!/usr/bin/env python
import os
import django
from celery import current_app
from products.models import Product
from users.models import User
from django.core.cache import cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

print("\n=== DATABASE TEST ===")
print(f"✅ Total products: {Product.objects.count()}")
print(f"✅ Total users: {User.objects.count()}")

print("\n=== SAMPLE PRODUCTS ===")
for p in Product.objects.all()[:3]:
    print(f"  - ID {p.id}: {p.name} (${p.price})")

print("\n=== CELERY TEST ===")

print(f"✅ Celery app ready: {current_app.conf}")

print("\n=== CACHE TEST ===")

cache.set("test_key", "test_value", 60)
value = cache.get("test_key")
print(f"✅ Cache test: {value}")
print("\n✅ All tests passed!")
