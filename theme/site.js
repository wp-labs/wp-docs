(function() {
    function buildTopbar() {
        const menuBar = document.getElementById('mdbook-menu-bar');
        if (!menuBar || menuBar.querySelector('.wp-topbar')) {
            return;
        }

        const rightButtons = menuBar.querySelector('.right-buttons');
        const topbar = document.createElement('div');
        topbar.className = 'wp-topbar';

        const title = document.documentElement.lang === 'zh-CN' ? '文档站' : 'Docs';
        topbar.innerHTML = `<span class="wp-chip">${title}</span>`;

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
        document.addEventListener('DOMContentLoaded', buildTopbar);
    } else {
        buildTopbar();
    }

    window.addEventListener('load', buildTopbar);
})();
