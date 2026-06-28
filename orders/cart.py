from __future__ import annotations

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from products.models import Product
from .models import CartItem

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.is_authenticated = self.user.is_authenticated
        
        # Если гость, инициализируем простую сессию {product_id: quantity}
        if not self.is_authenticated:
            if CART_SESSION_KEY not in self.request.session:
                self.request.session[CART_SESSION_KEY] = {}
            self.session_cart = self.request.session[CART_SESSION_KEY]

    def add(self, product: Product, quantity: int = 1, *, replace: bool = False) -> CartItem | None:
        if self.is_authenticated:
            # --- ЛОГИКА ДЛЯ БАЗЫ ДАННЫХ ---
            with transaction.atomic():
                item, created = CartItem.objects.select_for_update().get_or_create(
                    user=self.user,
                    product=product,
                    defaults={"quantity": 1, "total_price": product.price}
                )

                if replace:
                    new_quantity = quantity
                else:
                    # ИСПРАВЛЕНО: Если запись создана с нуля, берем переданный quantity.
                    # Если запись уже была, корректно суммируем старое количество и новое.
                    new_quantity = quantity if created else item.quantity + quantity

                if new_quantity > product.stock:
                    new_quantity = product.stock

                if new_quantity <= 0:
                    item.delete()
                    return None

                item.quantity = new_quantity
                item.total_price = Decimal(new_quantity) * product.price
                item.save(update_fields=["quantity", "total_price"])
                return item
        else:
            # --- ЛОГИКА ДЛЯ СЕССИИ (Храним только ID: quantity) ---
            product_id = str(product.id)
            current_quantity = self.session_cart.get(product_id, 0)
            
            new_quantity = quantity if replace else current_quantity + quantity

            if new_quantity > product.stock:
                new_quantity = product.stock

            if new_quantity <= 0:
                self.session_cart.pop(product_id, None)
                self.save_session()
                return None

            self.session_cart[product_id] = new_quantity
            self.save_session()
            return None


    def set_quantity(self, product: Product, quantity: int) -> CartItem | None:
        if quantity <= 0:
            self.remove(product)
            return None
        return self.add(product, quantity, replace=True)
    
    def remove(self, product: Product) -> None:
        if self.is_authenticated:
            CartItem.objects.filter(user=self.user, product=product).delete()
        else:
            self.session_cart.pop(str(product.id), None)
            self.save_session()
            
    def clear(self) -> None:
        if self.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        else:
            self.request.session.pop(CART_SESSION_KEY, None)
            self.save_session()    
    
    def save_session(self) -> None:
        self.request.session.modified = True

    def merge_session_cart(self) -> None:
        """Переносит легковесную корзину из сессии в БД после авторизации."""
        if not self.request.user.is_authenticated or CART_SESSION_KEY not in self.request.session:
            return

        session_cart = self.request.session[CART_SESSION_KEY]
        if not session_cart:
            return

        product_ids = list(session_cart.keys())
        products_map = Product.objects.in_bulk(product_ids)

        with transaction.atomic():
            for product_id, session_quantity in session_cart.items():
                product = products_map.get(int(product_id))
                if not product:
                    continue  # Защита, если товар удален из БД

                item, created = CartItem.objects.select_for_update().get_or_create(
                    user=self.request.user,
                    product=product,
                    defaults={
                        "quantity": session_quantity, 
                        "total_price": product.price * session_quantity
                    }
                )
                
                if not created:
                    new_quantity = item.quantity + session_quantity
                    
                    if new_quantity > product.stock:
                        new_quantity = product.stock

                    if new_quantity <= 0:
                        item.delete()
                        continue

                    item.quantity = new_quantity
                    item.total_price = Decimal(new_quantity) * product.price
                    item.save(update_fields=["quantity", "total_price"])

        # Очищаем сессию, так как все данные перенесены в БД
        self.request.session.pop(CART_SESSION_KEY, None)
        self.save_session()

    def __iter__(self):
        """Возвращает генератор словарей для удобного цикла во views и шаблонах."""
        if self.is_authenticated:
            # Для авторизованных тянем данные из БД (с оптимизацией select_related)
            items = CartItem.objects.filter(user=self.user).select_related("product").order_by("id")
            for item in items:
                yield {
                    "product": item.product,
                    "quantity": item.quantity,
                    "subtotal": item.total_price
                }
        else:
            # Для гостей собираем данные «на лету» по ID из сессии
            product_ids = list(self.session_cart.keys())
            products_map = Product.objects.in_bulk(product_ids)
            
            for product_id, qty in self.session_cart.items():
                product = products_map.get(int(product_id))
                if not product:
                    continue
                yield {
                    "product": product,
                    "quantity": qty,
                    "subtotal": product.price * qty
                }

    def __len__(self) -> int:
        """Позволяет использовать len(cart) для получения общего количества товаров."""
        if self.is_authenticated:
            result = CartItem.objects.filter(user=self.user).aggregate(
                total_count=Coalesce(Sum("quantity"), 0)
            )
            return result["total_count"]
        else:
            return sum(self.session_cart.values())

    @property
    def total(self) -> Decimal:
        """Позволяет получать общую стоимость корзины через cart.total."""
        if self.is_authenticated:
            result = CartItem.objects.filter(user=self.user).aggregate(
                total=Coalesce(Sum("total_price"), Decimal("0.00"))
            )
            return result["total"]
        else:
            product_ids = list(self.session_cart.keys())
            products_map = Product.objects.in_bulk(product_ids)
            return sum(
                (p.price * self.session_cart[str(p.id)] for p in products_map.values()), 
                Decimal("0.00")
            )
