document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('filter-form');

    if (!form) return;

    // ---------------------------
    // CHECKBOX FILTER
    // ---------------------------
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');

    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            form.submit();
        });
    });

    // ---------------------------
    // REMOVE KEYWORDS (chips)
    // ---------------------------
    const keywordsList = document.querySelector('.keywords-list');

    if (keywordsList) {

        keywordsList.addEventListener('click', e => {

            const icon = e.target.closest('.remove-keyword-icon');
            if (!icon) return;

            const tag = icon.closest('.keyword-tag');
            const slug = tag.dataset.keyword;

            const checkbox = form.querySelector(
                `input[value="${slug}"]`
            );

            if (checkbox) {
                checkbox.checked = false;
                form.submit();
            }
        });
    }

});