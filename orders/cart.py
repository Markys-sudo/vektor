from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from products.models import Product
from .models import CartItem


class Cart:
    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def add_to_cart(self, product: Product, quantity: int = 1, *, replace: bool = False) -> CartItem | None:
        # Задаємо дефолтне значення 1, щоб не порушувати констреінт бази даних
        item, created = CartItem.objects.select_for_update().get_or_create(
            user=self.user,
            product=product,
            defaults={"quantity": 1, "total_price": product.price}
        )

        # Розраховуємо нову кількість
        if replace:
            new_quantity = quantity
        else:
            # Якщо об'єкт щойно створено, його поточна кількість у базі вже дорівнює 1 (з defaults).
            # Але користувач просив додати `quantity` (зазвичай 1 або більше).
            # Тому для нового об'єкта ми беремо просто `quantity`, а для старого — додаємо.
            new_quantity = quantity if created else item.quantity + quantity

        # Валідація залишків на складі
        if new_quantity > product.stock:
            new_quantity = product.stock

        # Якщо кількість <= 0, видаляємо товар з кошика
        if new_quantity <= 0:
            if not created:  # Якщо об'єкт вже існував у базі, видаляємо його
                item.delete()
            elif created:
                # Якщо ми його щойно створили (наприклад, передали від'ємне значення), 
                # але база його вже зберегла з quantity=1, видаляємо його назад
                item.delete()
            return None

        # Оновлюємо поля та зберігаємо
        item.quantity = new_quantity
        item.total_price = Decimal(new_quantity) * product.price
        item.save(update_fields=["quantity", "total_price"])
        
        return item
    
    def set_quantity(self, product: Product, quantity: int) -> CartItem | None:
        return self.add_to_cart(product, quantity, replace=True)
    
    def remove(self, product: Product) -> None:
        CartItem.objects.filter(user=self.user, product=product).delete()
            
    def clear(self) -> None:
        CartItem.objects.filter(user=self.user).delete()    
    
    def items(self):
        return CartItem.objects.filter(user=self.user).select_related("product")
    
    def total_price(self) -> Decimal:
        # Агрегація на рівні БД для обчислення загальної вартості товарів у кошику
        result = self.items().aggregate(
            total=Coalesce(Sum("total_price"), Decimal("0.00"))
        )
        return result["total"]
        
    def count(self) -> int:
        # Рахуємо суму кількостей товарів безпосередньо в БД
        result = self.items().aggregate(
            total_count=Coalesce(Sum("quantity"), 0)
        )
        return result["total_count"]