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

        const versionText = version === 'alpha' ? 'ALPHA 开发版' : 'BETA 预发布版';
        const versionTextEn = version === 'alpha' ? 'ALPHA Development Version' : 'BETA Pre-release Version';

        // Detect language
        const isZh = document.documentElement.lang === 'zh-CN';
        const displayText = isZh ? versionText : versionTextEn;
        const stableText = isZh ? '查看稳定版' : 'View Stable Version';

        banner.innerHTML = `
            ⚠️ ${displayText} -
            <a href="/">${stableText}</a>
        `;

        document.body.insertBefore(banner, document.body.firstChild);
        document.body.classList.add('has-version-banner');
    }
})();
