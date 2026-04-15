(function() {
    function isZhPage() {
        const lang = (document.documentElement.lang || '').toLowerCase();
        return lang.startsWith('zh');
    }

    function parseDocPath() {
        const parts = window.location.pathname.split('/').filter(Boolean);
        const versionIndex = parts.findIndex(part => part === 'alpha' || part === 'beta');
        const langIndex = parts.findIndex(part => part === 'zh' || part === 'en');
        const version = versionIndex >= 0 ? parts[versionIndex] : 'stable';
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

        return {
            baseParts: parts.slice(0, versionIndex >= 0 ? versionIndex : 0),
            version,
            langInPath: false,
            currentLang,
            pageParts: parts.slice(versionIndex >= 0 ? versionIndex + 1 : 0)
        };
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

    const parsedPath = parseDocPath();

    fetch(buildVersionFilePath(parsedPath))
        .then(response => response.ok ? response.text() : Promise.reject())
        .then(wpVersion => {
            renderBanner(wpVersion.trim(), parsedPath);
        })
        .catch(() => {
            renderBanner(null, parsedPath);
        });

    function renderBanner(wpVersion, parsed) {
        const banner = document.createElement('div');
        banner.className = `version-banner ${parsed.version}`;

        const isZh = isZhPage();
        const versionInfo = wpVersion
            ? `<span class="version-info">WarpParse ${wpVersion}</span>`
            : '';

        const versions = [
            { key: 'stable', label: isZh ? '稳定版' : 'Stable' },
            { key: 'beta', label: 'Beta' },
            { key: 'alpha', label: 'Alpha' }
        ];

        const versionLinks = versions.map(version => {
            const currentClass = version.key === parsed.version ? ' current' : '';
            const disabledClass = parsed.langInPath ? '' : ' disabled';
            const href = buildVersionPath(version.key, parsed);
            return `<a href="${href}" class="version-link${currentClass}${disabledClass}">${version.label}</a>`;
        }).join('');

        banner.innerHTML = `
            <div class="banner-content">
                ${versionInfo}
                <div class="version-switcher">
                    ${versionLinks}
                </div>
            </div>
        `;

        document.body.insertBefore(banner, document.body.firstChild);
        document.body.classList.add('has-version-banner');
    }
})();
