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
        if (!menuBar) {
            return;
        }

        if (menuBar.querySelector('.wp-topbar')) {
            moveTopbarItems(menuBar.querySelector('.wp-topbar'));
            return;
        }

        const rightButtons = menuBar.querySelector('.right-buttons');
        const topbar = document.createElement('div');
        topbar.className = 'wp-topbar';

        topbar.innerHTML = '<span class="wp-chip">Warp Parse</span>';

        if (rightButtons) {
            menuBar.insertBefore(topbar, rightButtons);
            moveTopbarItems(topbar);
        }
    }

    function moveTopbarItems(topbar) {
        if (!topbar) {
            return;
        }

        const banner = document.querySelector('.version-banner');
        if (banner && banner.parentElement !== topbar) {
            topbar.insertBefore(banner, topbar.firstChild);
        }

        const langSwitcher = document.querySelector('.lang-switcher');
        if (langSwitcher && langSwitcher.parentElement !== topbar) {
            topbar.appendChild(langSwitcher);
        }
    }

    function watchTopbarItems() {
        if (!window.MutationObserver) {
            return;
        }

        const observer = new MutationObserver(function() {
            buildTopbar();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            normalizeTheme();
            buildTopbar();
            watchTopbarItems();
        });
    } else {
        normalizeTheme();
        buildTopbar();
        watchTopbarItems();
    }

    window.addEventListener('load', function() {
        normalizeTheme();
        buildTopbar();
    });
})();
