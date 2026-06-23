"""Cart and checkout web views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from products.models import Product

from .cart import Cart
from .exceptions import OutOfStockError
from .forms import CheckoutForm
from .services import CartLine, create_order


def cart_detail(request):
    return render(request, "orders/cart.html", {"cart": Cart(request)})


def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.active(), id=product_id)
    Cart(request).add(product, int(request.POST.get("quantity", 1)))
    messages.success(request, f"«{product.name}» добавлен в корзину.")
    return redirect("orders:cart_detail")


def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Cart(request).set_quantity(product, int(request.POST.get("quantity", 1)))
    return redirect("orders:cart_detail")


def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Cart(request).remove(product)
    return redirect("orders:cart_detail")


class CheckoutView(LoginRequiredMixin, View):
    """Thin view over orders.services.create_order — no business logic here."""

    template_name = "orders/checkout.html"

    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect("orders:cart_detail")
        return render(request, self.template_name, {"cart": cart, "form": CheckoutForm()})

    def post(self, request):
        print("POST CHECKOUT")
        print(request.POST)
        cart = Cart(request)
        if len(cart) == 0:
            return redirect("orders:cart_detail")
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"cart": cart, "form": form})

        lines = [CartLine(product_id=int(pid), quantity=qty) for pid, qty in cart.cart.items()]
        try:
            order = create_order(
                user=request.user,
                lines=lines,
                shipping_address=(
                    f"{form.cleaned_data['full_name']}, тел. {form.cleaned_data['phone']}, "
                    f"{form.cleaned_data['city']}, {form.cleaned_data['address']}"
                ),
            )
        except OutOfStockError as exc:
            messages.error(request, str(exc))
            return redirect("orders:cart_detail")

        cart.clear()
        messages.success(request, f"Заказ #{order.pk} оформлен!")
        return redirect("users:order_history")
