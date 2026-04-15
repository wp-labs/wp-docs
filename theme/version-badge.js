(function() {
    // Detect version from URL path
    const path = window.location.pathname;
    let currentVersion = 'stable';

    if (path.includes('/alpha/')) {
        currentVersion = 'alpha';
    } else if (path.includes('/beta/')) {
        currentVersion = 'beta';
    }

    // Detect language (zh or en)
    let currentLang = 'zh';
    if (path.includes('/en/')) {
        currentLang = 'en';
    }

    // Fetch WarpParse version from wp-version.txt
    const versionPath = currentVersion === 'stable'
        ? '/wp-version.txt'
        : `/${currentVersion}/wp-version.txt`;

    fetch(versionPath)
        .then(response => response.ok ? response.text() : Promise.reject())
        .then(wpVersion => {
            wpVersion = wpVersion.trim();
            renderBanner(wpVersion);
        })
        .catch(() => {
            // Fallback if version file not found
            renderBanner(null);
        });

    function renderBanner(wpVersion) {
        const banner = document.createElement('div');
        banner.className = `version-banner ${currentVersion}`;

        const isZh = document.documentElement.lang === 'zh-CN';

        // Add version info if available
        const versionInfo = wpVersion
            ? `<span class="version-info">WarpParse ${wpVersion}</span>`
            : '';

        // Build version switcher links
        const versions = [
            { key: 'stable', label: isZh ? '稳定版' : 'Stable', path: `/${currentLang}/` },
            { key: 'beta', label: 'Beta', path: `/beta/${currentLang}/` },
            { key: 'alpha', label: 'Alpha', path: `/alpha/${currentLang}/` }
        ];

        const versionLinks = versions.map(v => {
            const currentClass = v.key === currentVersion ? ' current' : '';
            return `<a href="${v.path}" class="version-link${currentClass}">${v.label}</a>`;
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
