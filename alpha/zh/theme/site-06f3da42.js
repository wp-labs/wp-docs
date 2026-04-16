(function() {
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

    function simplifyThemeMenu() {
        const labels = {
            'mdbook-theme-default_theme': 'Auto',
            'mdbook-theme-light': 'Light',
            'mdbook-theme-navy': 'Dark'
        };
        const hiddenThemes = [
            'mdbook-theme-rust',
            'mdbook-theme-coal',
            'mdbook-theme-ayu'
        ];

        Object.keys(labels).forEach(function(id) {
            const item = document.getElementById(id);
            if (item) {
                item.textContent = labels[id];
            }
        });

        hiddenThemes.forEach(function(id) {
            const item = document.getElementById(id);
            if (item && item.parentElement) {
                item.parentElement.style.display = 'none';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            buildTopbar();
            simplifyThemeMenu();
            watchTopbarItems();
        });
    } else {
        buildTopbar();
        simplifyThemeMenu();
        watchTopbarItems();
    }

    window.addEventListener('load', function() {
        buildTopbar();
        simplifyThemeMenu();
    });
})();
