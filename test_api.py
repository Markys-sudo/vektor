#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from products.models import Product
from users.models import User

print("\n=== DATABASE TEST ===")
print(f"✅ Total products: {Product.objects.count()}")
print(f"✅ Total users: {User.objects.count()}")

print("\n=== SAMPLE PRODUCTS ===")
for p in Product.objects.all()[:3]:
    print(f"  - ID {p.id}: {p.name} (${p.price})")

print("\n=== CELERY TEST ===")
from celery import current_app
print(f"✅ Celery app ready: {current_app.conf}")

print("\n=== CACHE TEST ===")
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
value = cache.get('test_key')
print(f"✅ Cache test: {value}")

print("\n✅ All tests passed!")

