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

    // Create banner for all versions
    const banner = document.createElement('div');
    banner.className = `version-banner ${currentVersion}`;

    let badgeText, descText;
    const isZh = document.documentElement.lang === 'zh-CN';

    if (currentVersion === 'alpha') {
        badgeText = 'ALPHA';
        descText = isZh ? '最新开发版 - 包含最新特性' : 'Latest Development Version - Contains newest features';
    } else if (currentVersion === 'beta') {
        badgeText = 'BETA';
        descText = isZh ? '预发布版 - 即将正式发布' : 'Pre-release Version - Coming soon to stable';
    } else {
        badgeText = isZh ? '稳定版' : 'STABLE';
        descText = isZh ? '生产环境推荐使用' : 'Recommended for production';
    }

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
            <span class="badge">${badgeText}</span>
            <span>${descText}</span>
            <div class="version-switcher">
                ${versionLinks}
            </div>
        </div>
    `;

    document.body.insertBefore(banner, document.body.firstChild);
    document.body.classList.add('has-version-banner');
})();
