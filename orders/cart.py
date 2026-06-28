from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from products.models import Product
from .models import CartItem


class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user
        # Проверяем, авторизован ли пользователь
        self.is_authenticated = self.user.is_authenticated
        
        # Если это гость, инициализируем корзину в сессии
        if not self.is_authenticated:
            if 'cart' not in self.request.session:
                self.request.session['cart'] = {}
            self.session_cart = self.request.session['cart']

    def add_to_cart(self, product: Product, quantity: int = 1, *, replace: bool = False) -> CartItem | None:
        if self.is_authenticated:
            # --- ЛОГИКА ДЛЯ АВТОРИЗОВАННЫХ (БАЗА ДАННЫХ) ---
            with transaction.atomic():
                item, created = CartItem.objects.select_for_update().get_or_create(
                    user=self.user,
                    product=product,
                    defaults={"quantity": 1, "total_price": product.price}
                )

                if replace:
                    new_quantity = quantity
                else:
                    new_quantity = quantity if created else item.quantity + quantity

                if new_quantity > product.stock:
                    new_quantity = product.stock

                if new_quantity <= 0:
                    if not created:
                        item.delete()
                    return None

                item.quantity = new_quantity
                item.total_price = Decimal(new_quantity) * product.price
                item.save(update_fields=["quantity", "total_price"])
                return item
        else:
            # --- ЛОГИКА ДЛЯ ГОСТЕЙ (СЕССИЯ / КЭШ) ---
            product_id = str(product.id)
            
            if replace:
                new_quantity = quantity
            else:
                current_quantity = self.session_cart.get(product_id, {}).get('quantity', 0)
                new_quantity = current_quantity + quantity

            if new_quantity > product.stock:
                new_quantity = product.stock

            if new_quantity <= 0:
                if product_id in self.session_cart:
                    del self.session_cart[product_id]
                self.request.session.modified = True
                return None

            # Сохраняем данные товара в сессию
            self.session_cart[product_id] = {
                'quantity': new_quantity,
                'price': str(product.price),
                'total_price': str(Decimal(new_quantity) * product.price)
            }
            self.request.session.modified = True
            return None

    def set_quantity(self, product: Product, quantity: int) -> CartItem | None:
        return self.add_to_cart(product, quantity, replace=True)
    
    def remove(self, product: Product) -> None:
        if self.is_authenticated:
            CartItem.objects.filter(user=self.user, product=product).delete()
        else:
            product_id = str(product.id)
            if product_id in self.session_cart:
                del self.session_cart[product_id]
                self.request.session.modified = True
            
    def clear(self) -> None:
        if self.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        else:
            self.request.session['cart'] = {}
            self.request.session.modified = True    
    
    def items(self):
        if self.is_authenticated:
            return CartItem.objects.filter(user=self.user).select_related("product")
        else:
            # Для гостей собираем список "виртуальных" объектов из сессии
            product_ids = self.session_cart.keys()
            products = Product.objects.filter(id__in=product_ids)
            
            cart_items = []
            for product in products:
                session_item = self.session_cart[str(product.id)]
                # ПРАВИЛЬНО: явно указываем user=None для изоляции анонимного пользователя
                item = CartItem(
                    user=None,  
                    product=product,
                    quantity=session_item['quantity'],
                    total_price=Decimal(session_item['total_price'])
                )
                cart_items.append(item)
            return cart_items

    def total_price(self) -> Decimal:
        if self.is_authenticated:
            result = CartItem.objects.filter(user=self.user).aggregate(
                total=Coalesce(Sum("total_price"), Decimal("0.00"))
            )
            return result["total"]
        else:
            return sum(Decimal(item['total_price']) for item in self.session_cart.values())
        
    def count(self) -> int:
        if self.is_authenticated:
            result = CartItem.objects.filter(user=self.user).aggregate(
                total_count=Coalesce(Sum("quantity"), 0)
            )
            return result["total_count"]
        else:
            return sum(item['quantity'] for item in self.session_cart.values())
