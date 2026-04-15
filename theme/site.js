(function() {
    function normalizeTheme() {
        try {
            const stored = localStorage.getItem('mdbook-theme');
            if (!stored) {
                return;
            }
            if (stored === 'ayu' || stored === 'navy' || stored === 'coal' || stored === 'rust') {
                localStorage.setItem('mdbook-theme', 'light');
                const html = document.documentElement;
                html.classList.remove('ayu', 'navy', 'coal', 'rust');
                html.classList.add('light');
            }
        } catch (e) { }
    }

    function buildTopbar() {
        const menuBar = document.getElementById('mdbook-menu-bar');
        if (!menuBar || menuBar.querySelector('.wp-topbar')) {
            return;
        }

        const rightButtons = menuBar.querySelector('.right-buttons');
        const topbar = document.createElement('div');
        topbar.className = 'wp-topbar';

        topbar.innerHTML = '<span class="wp-chip">Warp Parse</span>';

        if (rightButtons) {
            menuBar.insertBefore(topbar, rightButtons);
            const langSwitcher = document.querySelector('.lang-switcher');
            if (langSwitcher) {
                topbar.appendChild(langSwitcher);
            }
            const banner = document.querySelector('.version-banner');
            if (banner) {
                topbar.insertBefore(banner, topbar.firstChild);
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            normalizeTheme();
            buildTopbar();
        });
    } else {
        normalizeTheme();
        buildTopbar();
    }

    window.addEventListener('load', function() {
        normalizeTheme();
        buildTopbar();
    });
})();
