(function() {
    const VERSION_KEYS = ['alpha', 'beta'];
    const LANG_KEYS = ['zh', 'en'];

    function isZhPage() {
        return (document.documentElement.lang || '').toLowerCase().startsWith('zh');
    }

    function normalizePagePath(pathname) {
        if (!pathname || pathname === '/') {
            return '/';
        }
        return pathname.endsWith('/') ? pathname : pathname.replace(/\/?$/, '');
    }

    function parseDocPath() {
        const parts = window.location.pathname.split('/').filter(Boolean);
        const versionIndex = parts.findIndex(part => VERSION_KEYS.includes(part));
        const langIndex = parts.findIndex(part => LANG_KEYS.includes(part));
        const currentLang = isZhPage() ? 'zh' : 'en';

        if (langIndex >= 0) {
            return {
                baseParts: parts.slice(0, versionIndex >= 0 ? versionIndex : langIndex),
                version: versionIndex >= 0 ? parts[versionIndex] : 'stable',
                langInPath: true,
                currentLang,
                pageParts: parts.slice(langIndex + 1)
            };
        }

        return {
            baseParts: parts.slice(0, versionIndex >= 0 ? versionIndex : 0),
            version: versionIndex >= 0 ? parts[versionIndex] : 'stable',
            langInPath: false,
            currentLang,
            pageParts: parts.slice(versionIndex >= 0 ? versionIndex + 1 : 0)
        };
    }

    function buildLangPath(targetLang, parsed) {
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

    function buildVersionPath(targetVersion, parsed) {
        const prefix = parsed.baseParts.length ? '/' + parsed.baseParts.join('/') : '';
        const versionPrefix = targetVersion === 'stable' ? '' : '/' + targetVersion;

        if (!parsed.langInPath) {
            return targetVersion === parsed.version ? '/' : '#';
        }

        return prefix + versionPrefix + '/' + parsed.currentLang + '/';
    }

    function buildVersionFilePath(parsed) {
        const prefix = parsed.baseParts.length ? '/' + parsed.baseParts.join('/') : '';
        const versionPrefix = parsed.version === 'stable' ? '' : '/' + parsed.version;
        return prefix + versionPrefix + '/wp-version.txt';
    }

    function byAnyId(ids) {
        for (const id of ids) {
            const element = document.getElementById(id);
            if (element) {
                return element;
            }
        }
        return null;
    }

    function ensureTopbar() {
        const menuBar = byAnyId(['menu-bar', 'mdbook-menu-bar']);
        if (!menuBar) {
            return null;
        }

        let topbar = menuBar.querySelector('.wp-topbar');
        if (topbar) {
            return topbar;
        }

        const rightButtons = menuBar.querySelector('.right-buttons');
        if (!rightButtons) {
            return null;
        }

        topbar = document.createElement('div');
        topbar.className = 'wp-topbar';
        topbar.innerHTML = '<span class="wp-chip">Warp Parse</span>';
        menuBar.insertBefore(topbar, rightButtons);
        return topbar;
    }

    function refreshTopbar() {
        const topbar = ensureTopbar();
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

    function renderLangSwitcher(parsed) {
        if (document.querySelector('.lang-switcher')) {
            return;
        }

        const currentLang = parsed.currentLang;
        const switcher = document.createElement('div');
        switcher.className = 'lang-switcher';

        const zh = currentLang === 'zh' ? document.createElement('span') : document.createElement('a');
        zh.textContent = '中文';
        if (currentLang === 'zh') {
            zh.className = 'current';
        } else {
            zh.href = buildLangPath('zh', parsed);
        }

        const sep = document.createElement('span');
        sep.className = 'lang-sep';
        sep.textContent = '|';

        const en = currentLang === 'en' ? document.createElement('span') : document.createElement('a');
        en.textContent = 'English';
        if (currentLang === 'en') {
            en.className = 'current';
        } else {
            en.href = buildLangPath('en', parsed);
        }

        switcher.append(zh, sep, en);
        document.body.appendChild(switcher);
    }

    function renderVersionBanner(wpVersion, parsed) {
        if (document.querySelector('.version-banner')) {
            return;
        }

        const banner = document.createElement('div');
        const isZh = parsed.currentLang === 'zh';
        const versions = [
            { key: 'stable', label: isZh ? '稳定版' : 'Stable' },
            { key: 'beta', label: 'Beta' },
            { key: 'alpha', label: 'Alpha' }
        ];
        const versionInfo = wpVersion ? `<span class="version-info">WarpParse ${wpVersion}</span>` : '';
        const versionLinks = versions.map(version => {
            const currentClass = version.key === parsed.version ? ' current' : '';
            const disabledClass = parsed.langInPath ? '' : ' disabled';
            return `<a href="${buildVersionPath(version.key, parsed)}" class="version-link${currentClass}${disabledClass}">${version.label}</a>`;
        }).join('');

        banner.className = `version-banner ${parsed.version}`;
        banner.innerHTML = `<div class="banner-content">${versionInfo}<div class="version-switcher">${versionLinks}</div></div>`;
        document.body.insertBefore(banner, document.body.firstChild);
        document.body.classList.add('has-version-banner');
        refreshTopbar();
    }

    function loadVersionBanner(parsed) {
        fetch(buildVersionFilePath(parsed))
            .then(response => response.ok ? response.text() : Promise.reject())
            .then(wpVersion => renderVersionBanner(wpVersion.trim(), parsed))
            .catch(() => renderVersionBanner(null, parsed));
    }

    function simplifyThemeMenu() {
        const labels = {
            'default_theme': 'Auto',
            'mdbook-theme-default_theme': 'Auto',
            'light': 'Light',
            'mdbook-theme-light': 'Light',
            'navy': 'Dark',
            'mdbook-theme-navy': 'Dark'
        };
        const hiddenThemes = ['rust', 'coal', 'ayu', 'mdbook-theme-rust', 'mdbook-theme-coal', 'mdbook-theme-ayu'];

        Object.keys(labels).forEach(id => {
            const item = document.getElementById(id);
            if (item) {
                item.textContent = labels[id];
            }
        });

        hiddenThemes.forEach(id => {
            const item = document.getElementById(id);
            if (item && item.parentElement) {
                item.parentElement.hidden = true;
            }
        });
    }

    function currentMermaidTheme() {
        const html = document.documentElement;
        return html.classList.contains('ayu') || html.classList.contains('navy') || html.classList.contains('coal')
            ? 'dark'
            : 'default';
    }

    function bindMermaidThemeReload() {
        const wasDark = currentMermaidTheme() === 'dark';
        ['light', 'rust', 'navy', 'coal', 'ayu', 'mdbook-theme-light', 'mdbook-theme-rust', 'mdbook-theme-navy', 'mdbook-theme-coal', 'mdbook-theme-ayu'].forEach(id => {
            const item = document.getElementById(id);
            if (!item) {
                return;
            }
            item.addEventListener('click', function() {
                const willBeDark = id === 'navy' || id === 'coal' || id === 'ayu'
                    || id === 'mdbook-theme-navy' || id === 'mdbook-theme-coal' || id === 'mdbook-theme-ayu';
                if (wasDark !== willBeDark) {
                    window.location.reload();
                }
            }, { once: true });
        });
    }

    function loadMermaidIfNeeded() {
        if (!document.querySelector('.mermaid')) {
            return;
        }

        const script = document.createElement('script');
        const siteScript = document.currentScript || document.querySelector('script[src*="/theme/site"], script[src*="theme/site"]');
        const siteScriptUrl = siteScript && siteScript.src ? siteScript.src : '';
        const docsRoot = siteScriptUrl
            ? new URL('../', siteScriptUrl).toString()
            : new URL('./', document.baseURI).toString();

        script.src = new URL('mermaid.min.js', docsRoot).toString();
        script.defer = true;
        script.onload = function() {
            if (!window.mermaid) {
                return;
            }
            window.mermaid.initialize({
                startOnLoad: true,
                theme: currentMermaidTheme()
            });
            bindMermaidThemeReload();
        };
        document.head.appendChild(script);
    }

    function pageTocText(header) {
        const anchor = header.querySelector('a.header');
        return (anchor || header).textContent.trim();
    }

    function buildPageToc() {
        const main = document.querySelector('main');
        if (!main) {
            return;
        }

        const headers = Array.from(main.querySelectorAll('h2, h3')).filter(header => {
            return header.id && pageTocText(header);
        });

        if (headers.length < 4 || document.querySelector('.page-toc')) {
            return;
        }

        const nav = document.createElement('nav');
        nav.className = 'page-toc';
        nav.setAttribute('aria-label', '本页目录');

        const title = document.createElement('div');
        title.className = 'page-toc-title';
        title.textContent = '本页目录';
        nav.appendChild(title);

        const list = document.createElement('ol');
        nav.appendChild(list);

        headers.forEach(header => {
            const item = document.createElement('li');
            item.className = 'page-toc-' + header.tagName.toLowerCase();

            const link = document.createElement('a');
            link.href = '#' + header.id;
            link.textContent = pageTocText(header);

            item.appendChild(link);
            list.appendChild(item);
        });

        document.body.appendChild(nav);

        const links = Array.from(nav.querySelectorAll('a'));

        function placeToc() {
            const mainRect = main.getBoundingClientRect();
            const tocWidth = 320;
            const gap = 42;
            const viewportPadding = 24;
            const preferredLeft = mainRect.right + gap;
            const maxLeft = window.innerWidth - tocWidth - viewportPadding;
            nav.style.left = Math.max(viewportPadding, Math.min(preferredLeft, maxLeft)) + 'px';
        }

        function setActive() {
            let active = headers[0];
            for (const header of headers) {
                if (header.getBoundingClientRect().top <= 120) {
                    active = header;
                } else {
                    break;
                }
            }

            links.forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === '#' + active.id);
            });
        }

        placeToc();
        setActive();
        window.addEventListener('resize', placeToc);
        document.addEventListener('scroll', placeToc, { passive: true });
        document.addEventListener('scroll', setActive, { passive: true });
    }

    function initCollapsibleSidebar() {
        const storageKey = 'wp-docs-sidebar-state';

        function getState() {
            try {
                return JSON.parse(localStorage.getItem(storageKey)) || {};
            } catch {
                return {};
            }
        }

        function saveState(state) {
            try {
                localStorage.setItem(storageKey, JSON.stringify(state));
            } catch {
                // Ignore storage failures.
            }
        }

        function enhanceChapter(chapter) {
            if (!chapter || chapter.dataset.wpSidebarEnhanced === 'true') {
                return;
            }
            chapter.dataset.wpSidebarEnhanced = 'true';

            const state = getState();
            const activeLink = chapter.querySelector('a.active');
            if (activeLink) {
                let section = activeLink.closest('ol.section');
                while (section) {
                    const titleLi = section.parentElement;
                    const titleLink = titleLi && titleLi.querySelector(':scope > .chapter-link-wrapper a[href], :scope > a[href]');
                    if (titleLink) {
                        const key = titleLink.getAttribute('href') || titleLink.textContent.trim();
                        state[key] = true;
                    }
                    section = titleLi && titleLi.parentElement
                        ? titleLi.parentElement.closest('ol.section')
                        : null;
                }
                saveState(state);
            }

            chapter.querySelectorAll(':scope > li.chapter-item, ol.section > li.chapter-item').forEach(titleLi => {
                const childOl = titleLi.querySelector(':scope > ol.section');
                const linkWrapper = titleLi.querySelector(':scope > .chapter-link-wrapper');
                if (!childOl) {
                    return;
                }

                const link = titleLi.querySelector(':scope > .chapter-link-wrapper a[href], :scope > a[href]');
                if (!link) {
                    return;
                }

                const key = link.getAttribute('href') || link.textContent.trim();
                const hasActive = !!childOl.querySelector('a.active');

                let toggle = titleLi.querySelector(':scope > .chapter-link-wrapper .chapter-fold-toggle, :scope > .chapter-fold-toggle');
                if (!toggle) {
                    toggle = document.createElement('div');
                    toggle.className = 'chapter-fold-toggle';
                    toggle.setAttribute('role', 'button');
                    toggle.setAttribute('tabindex', '0');
                    toggle.setAttribute('aria-label', 'Toggle section');
                    toggle.innerHTML = '<div class="chapter-fold-chevron" aria-hidden="true"></div>';

                    const onToggle = event => {
                        event.preventDefault();
                        event.stopPropagation();
                        titleLi.classList.toggle('expanded');
                        state[key] = titleLi.classList.contains('expanded');
                        saveState(state);
                    };

                    toggle.addEventListener('click', onToggle);
                    toggle.addEventListener('keydown', event => {
                        if (event.key === 'Enter' || event.key === ' ') {
                            onToggle(event);
                        }
                    });

                    if (linkWrapper) {
                        linkWrapper.appendChild(toggle);
                    } else {
                        titleLi.appendChild(toggle);
                    }
                }

                let shouldExpand = hasActive;
                if (state[key] === true) {
                    shouldExpand = true;
                } else if (state[key] === false) {
                    shouldExpand = false;
                }
                titleLi.classList.toggle('expanded', shouldExpand);
            });
        }

        function tryInit() {
            const chapter = document.querySelector('.sidebar .chapter, .sidebar-scrollbox .chapter');
            if (chapter) {
                enhanceChapter(chapter);
                return true;
            }
            return false;
        }

        if (tryInit()) {
            return;
        }

        const observer = new MutationObserver(() => {
            if (tryInit()) {
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function init() {
        const parsed = parseDocPath();
        renderLangSwitcher(parsed);
        refreshTopbar();
        simplifyThemeMenu();
        loadVersionBanner(parsed);
        loadMermaidIfNeeded();
        initCollapsibleSidebar();
        buildPageToc();
    }

    window.wpDocsRefreshTopbar = refreshTopbar;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
