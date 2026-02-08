(function() {
    // Detect version from URL path
    const path = window.location.pathname;
    let version = null;

    if (path.includes('/alpha/')) {
        version = 'alpha';
    } else if (path.includes('/beta/')) {
        version = 'beta';
    }

    if (version) {
        // Create version banner
        const banner = document.createElement('div');
        banner.className = `version-banner ${version}`;

        let badgeText, descText, linkText;
        const isZh = document.documentElement.lang === 'zh-CN';

        if (version === 'alpha') {
            badgeText = 'ALPHA';
            descText = isZh ? '最新开发版 - 包含最新特性' : 'Latest Development Version - Contains newest features';
            linkText = isZh ? '访问稳定版' : 'View Stable Version';
        } else {
            badgeText = 'BETA';
            descText = isZh ? '预发布版 - 即将正式发布' : 'Pre-release Version - Coming soon to stable';
            linkText = isZh ? '访问稳定版' : 'View Stable Version';
        }

        banner.innerHTML = `
            <span class="badge">${badgeText}</span>
            ${descText}
            <a href="/">${linkText}</a>
        `;

        document.body.insertBefore(banner, document.body.firstChild);
        document.body.classList.add('has-version-banner');
    }
})();
