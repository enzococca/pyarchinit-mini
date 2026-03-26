/**
 * Universal Search - Typeahead & Keyboard Navigation
 */
(function() {
    const input = document.getElementById('universal-search-input');
    const dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;

    let debounceTimer = null;
    let activeIndex = -1;
    const typeIcons = {
        site: 'fas fa-map-marker-alt text-primary',
        us: 'fas fa-layer-group text-info',
        material: 'fas fa-gem text-warning',
        user: 'fas fa-user text-success'
    };
    const typeLabels = { site: 'Sites', us: 'US', material: 'Materials', user: 'People' };

    // Keyboard shortcut: / to focus search
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            input.focus();
            input.select();
        }
    });

    // Input handler with debounce
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const q = input.value.trim();
        if (q.length < 2) { hideDropdown(); return; }
        debounceTimer = setTimeout(() => fetchSuggestions(q), 300);
    });

    // Close on click outside
    document.addEventListener('click', function(e) {
        if (!input.closest('.pam-search-form').contains(e.target)) hideDropdown();
    });

    // Keyboard navigation
    input.addEventListener('keydown', function(e) {
        const items = dropdown.querySelectorAll('.pam-search-item');
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = Math.min(activeIndex + 1, items.length - 1);
            updateActive(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = Math.max(activeIndex - 1, -1);
            updateActive(items);
        } else if (e.key === 'Enter' && activeIndex >= 0 && items[activeIndex]) {
            e.preventDefault();
            window.location.href = items[activeIndex].href;
        } else if (e.key === 'Escape') {
            hideDropdown();
            input.blur();
        }
    });

    function updateActive(items) {
        items.forEach((el, i) => el.classList.toggle('active', i === activeIndex));
        if (activeIndex >= 0 && items[activeIndex]) {
            items[activeIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    function hideDropdown() {
        dropdown.style.display = 'none';
        dropdown.innerHTML = '';
        activeIndex = -1;
    }

    function fetchSuggestions(q) {
        fetch('/api/search/suggest?q=' + encodeURIComponent(q))
            .then(r => r.json())
            .then(data => {
                if (!data.length) { hideDropdown(); return; }
                renderSuggestions(data, q);
            })
            .catch(() => hideDropdown());
    }

    function renderSuggestions(items, query) {
        let html = '';
        let lastType = '';

        items.forEach(item => {
            if (item.type !== lastType) {
                html += `<div class="pam-search-category">${typeLabels[item.type] || item.type}</div>`;
                lastType = item.type;
            }
            const icon = typeIcons[item.type] || 'fas fa-circle';
            const label = highlightMatch(item.label || '', query);
            const sub = item.sub ? `<div class="search-sub">${highlightMatch(item.sub, query)}</div>` : '';
            html += `<a class="pam-search-item" href="${item.url}">
                <span class="search-icon"><i class="${icon}"></i></span>
                <span><span class="search-label">${label}</span>${sub}</span>
            </a>`;
        });

        // Add "View all results" link
        html += `<a class="pam-search-item" href="/search?q=${encodeURIComponent(query)}" style="justify-content:center;">
            <span class="search-label text-primary">View all results &rarr;</span>
        </a>`;

        dropdown.innerHTML = html;
        dropdown.style.display = 'block';
        activeIndex = -1;
    }

    function highlightMatch(text, query) {
        if (!query || !text) return text;
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark>$1</mark>');
    }
})();
