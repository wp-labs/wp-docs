// Language Switcher Script
(function() {
    function isZhPage() {
        const lang = (document.documentElement.lang || '').toLowerCase();
        return lang.startsWith('zh');
    }

    function normalizePagePath(pathname) {
        if (!pathname || pathname === '/') {
            return '/';
        }
        return pathname.endsWith('/') ? pathname : pathname.replace(/\/?$/, '');
    }

    function parseDocPath() {
        const parts = window.location.pathname.split('/').filter(Boolean);
        const versionIndex = parts.findIndex(part => part === 'alpha' || part === 'beta');
        const version = versionIndex >= 0 ? parts[versionIndex] : 'stable';
        const langIndex = parts.findIndex(part => part === 'zh' || part === 'en');
        const currentLang = isZhPage() ? 'zh' : 'en';

        if (langIndex >= 0) {
            return {
                baseParts: parts.slice(0, versionIndex >= 0 ? versionIndex : langIndex),
                version,
                langInPath: true,
                currentLang,
                pageParts: parts.slice(langIndex + 1)
            };
        }

        // Local `mdbook serve` for docs-zh/docs-en has no /zh or /en segment.
        return {
            baseParts: parts.slice(0, versionIndex >= 0 ? versionIndex : 0),
            version,
            langInPath: false,
            currentLang,
            pageParts: parts.slice(versionIndex >= 0 ? versionIndex + 1 : 0)
        };
    }

    function buildPath(targetLang) {
        const parsed = parseDocPath();
        const prefix = parsed.baseParts.length ? '/' + parsed.baseParts.join('/') : '';
        const versionPrefix = parsed.version === 'stable' ? '' : '/' + parsed.version;
        const page = parsed.pageParts.length ? '/' + parsed.pageParts.join('/') : '/';

        if (!parsed.langInPath) {
            if (targetLang === parsed.currentLang) {
                return normalizePagePath(page);
            }

            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                const port = targetLang === 'zh' ? '3000' : '3001';
                return window.location.protocol + '//' + window.location.hostname + ':' + port + normalizePagePath(page);
            }

            return '#';
        }

        return prefix + versionPrefix + '/' + targetLang + page;
    }

    function renderSwitcher() {
        const currentLang = isZhPage() ? 'zh' : 'en';
        const zhUrl = buildPath('zh');
        const enUrl = buildPath('en');

        const switcherHtml = `
            <div class="lang-switcher">
                ${currentLang === 'zh'
                    ? '<span class="current">中文</span> | <a href="' + enUrl + '">English</a>'
                    : '<a href="' + zhUrl + '">中文</a> | <span class="current">English</span>'
                }
            </div>
        `;

        const menuTitle = document.querySelector('.menu-title');
        if (menuTitle && menuTitle.parentNode && !document.querySelector('.lang-switcher')) {
            menuTitle.parentNode.insertAdjacentHTML('afterend', switcherHtml);
        }
    }

    renderSwitcher();
})();
