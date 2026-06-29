
class OwnerQuerysetMixin:
    """Limit the queryset to objects owned by the current user.

    Removes the duplicated ``filter(user=request.user)`` from both the web
    order history (Django ListView) and the orders API (DRF viewset). Works with
    any view exposing ``self.request`` and a ``get_queryset()`` in the MRO.
    """

    owner_field = "user"

    def get_queryset(self):
        base = super().get_queryset()  # type: ignore[misc]
        return base.filter(**{self.owner_field: self.request.user})  # type: ignore[attr-defined]
