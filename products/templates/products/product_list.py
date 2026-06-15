{% load catalog_extras %}

{% if is_paginated %}
<nav class="pagination">

    {% if page_obj.has_previous %}
        <a href="{% page_url page_obj.previous_page_number %}">← Prev</a>
    {% endif %}

    {% for num in page_obj.paginator.get_elided_page_range:page_obj.number %}
        {% if page_obj.number == num %}
            <span class="active">{{ num }}</span>
        {% else %}
            <a href="{% page_url num %}">{{ num }}</a>
        {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
        <a href="{% page_url page_obj.next_page_number %}">Next →</a>
    {% endif %}

</nav>
{% endif %}