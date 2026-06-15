from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    """Pagination URL that preserves the current filters/query params."""
    query = context["request"].GET.copy()
    query["page"] = page_number
    return "?" + query.urlencode()
