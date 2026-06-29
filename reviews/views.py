from django.shortcuts import redirect
from reviews.forms import ReviewForm
from reviews.models import Review
from reviews.services import has_purchased


class ReviewMixin:
    """Миксин для добавления отзывов на страницу DetailView товара."""

    def get_context_data(self, **kwargs):
        # Вызывает get_context_data у DetailView
        ctx = super().get_context_data(**kwargs)
        product = self.object
        # Загружаем отзывы для отображения в шаблоне
        ctx["reviews"] = product.reviews.select_related("user").order_by(
            "-created_at"
        )
        user = self.request.user
        ctx["can_review"] = (
            user.is_authenticated
            and has_purchased(user, product)
            and not Review.objects.filter(user=user, product=product).exists()
        )

        # Если форма уже передана (например, с ошибками из метода post), не перезаписываем её
        if "review_form" not in ctx:
            ctx["review_form"] = ReviewForm()

        return ctx

    def post(self, request, *args, **kwargs):
        # DetailView требует принудительного извлечения объекта в методе POST
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")

        if not has_purchased(request.user, self.object):
            return redirect(request.path)

        if Review.objects.filter(user=request.user, product=self.object).exists():
            return redirect(request.path)

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = self.object
            review.save()
            return redirect(request.path)

        # Если форма невалидна — рендерим страницу заново с ошибками
        ctx = self.get_context_data()
        ctx["review_form"] = form
        return self.render_to_response(ctx)

