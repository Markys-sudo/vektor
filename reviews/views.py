from django.shortcuts import render

from django.shortcuts import redirect
from reviews.forms import ReviewForm
from reviews.services import has_purchased
from reviews.models import Review

def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)

    product = self.object

    ctx["reviews"] = product.reviews.select_related("user").order_by("-created_at")
    ctx["review_form"] = ReviewForm()

    user = self.request.user

    ctx["can_review"] = (
        user.is_authenticated
        and has_purchased(user, product)
        and not Review.objects.filter(user=user, product=product).exists()
    )

    return ctx

def post(self, request, *args, **kwargs):
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