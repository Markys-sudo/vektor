document.addEventListener("DOMContentLoaded", () => {

    const params = new URLSearchParams(window.location.search);

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

            params.delete("page"); // reset pagination

            apply();
        });

    });


    // =========================
    // SORT
    // =========================
    document.querySelectorAll(".sort-button").forEach(btn => {

        btn.addEventListener("click", () => {

            params.set("sort", btn.dataset.sort);
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

            const q = document.querySelector('input[name="q"]').value;

            if (q) params.set("q", q);
            else params.delete("q");

            params.delete("page");

            apply();
        });
    }


    // =========================
    // KEYWORDS REMOVE (X)
    // =========================
    document.querySelectorAll(".remove-keyword-icon").forEach(icon => {

        icon.addEventListener("click", () => {

            const slug = icon.parentElement.dataset.keyword;

            let cats = params.getAll("category");

            cats = cats.filter(c => c !== slug);

            params.delete("category");

            cats.forEach(c => params.append("category", c));

            params.delete("page");

            apply();
        });

    });


    // =========================
    // SORT ACTIVE HIGHLIGHT
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