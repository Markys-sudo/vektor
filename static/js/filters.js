document.addEventListener("DOMContentLoaded", () => {

    const isProductsPage = document.querySelector(".product-grid");

    // 🔥 якщо це не сторінка товарів — виходимо
    if (!isProductsPage) return;

    const params = new URLSearchParams(window.location.search);

    // ❗ краще не перевантажувати сторінку одразу через string concat
    const apply = () => {
        window.location.search = params.toString();
    };

    // =========================
    // CATEGORY FILTER
    // =========================
    document.querySelectorAll('input[name="category"]').forEach(cb => {

        cb.addEventListener("change", () => {

            let cats = params.getAll("category");

            if (cb.checked) {
                if (!cats.includes(cb.value)) {
                    cats.push(cb.value);
                }
            } else {
                cats = cats.filter(c => c !== cb.value);
            }

            params.delete("category");

            cats.forEach(c => params.append("category", c));

            params.delete("page");

            apply();
        });

    });

    // =========================
    // SORT
    // =========================
    document.querySelectorAll(".sort-button").forEach(btn => {

        btn.addEventListener("click", () => {

            const sortValue = btn.dataset.sort;

            if (!sortValue) return;

            params.set("sort", sortValue);
            params.delete("page");

            apply();
        });

    });

    // =========================
    // SEARCH
    // =========================
    const searchBtn = document.getElementById("search-btn");

    if (searchBtn) {
        searchBtn.addEventListener("click", () => {

            const input = document.querySelector('input[name="q"]');

            if (!input) return;

            const q = input.value.trim();

            if (q) params.set("q", q);
            else params.delete("q");

            params.delete("page");

            apply();
        });
    }

    // =========================
    // KEYWORDS REMOVE
    // =========================
    document.querySelectorAll(".remove-keyword-icon").forEach(icon => {

        icon.addEventListener("click", () => {

            const parent = icon.closest(".keyword-tag");
            if (!parent) return;

            const slug = parent.dataset.keyword;

            let cats = params.getAll("category");

            cats = cats.filter(c => c !== slug);

            params.delete("category");
            cats.forEach(c => params.append("category", c));

            params.delete("page");

            apply();
        });

    });

    // =========================
    // SORT ACTIVE
    // =========================
    const currentSort = params.get("sort");

    if (currentSort) {
        document.querySelectorAll(".sort-button").forEach(btn => {
            if (btn.dataset.sort === currentSort) {
                btn.classList.add("active-sort");
            }
        });
    }

});