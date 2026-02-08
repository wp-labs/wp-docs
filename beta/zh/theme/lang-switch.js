// Language Switcher Script
(function() {
    const path = window.location.pathname;

    // Parse path: /basepath/lang/page.html
    // Example: /wp-docs/en/index.html -> basePath=/wp-docs, lang=en, page=/index.html
    let basePath = '';
    let currentLang = 'en';
    let currentPage = '/index.html';

    // Remove trailing slash for consistent matching
    const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;

    // Find where /zh/ or /en/ starts
    const zhIndex = cleanPath.indexOf('/zh/');
    const enIndex = cleanPath.indexOf('/en/');

    if (zhIndex !== -1 || enIndex !== -1) {
        const langIndex = zhIndex !== -1 ? zhIndex : enIndex;
        basePath = cleanPath.substring(0, langIndex);  // '/wp-docs' or ''
        currentLang = zhIndex !== -1 ? 'zh' : 'en';
        currentPage = cleanPath.substring(langIndex + 3);  // After '/zh' or '/en'
        if (!currentPage) {
            currentPage = '/index.html';
        }
    }

    // Build URLs
    const zhUrl = basePath + '/zh' + currentPage;
    const enUrl = basePath + '/en' + currentPage;

    // Create switcher HTML
    const switcherHtml = `
        <div class="lang-switcher">
            ${currentLang === 'zh'
                ? '<span class="current">中文</span> | <a href="' + enUrl + '">English</a>'
                : '<a href="' + zhUrl + '">中文</a> | <span class="current">English</span>'
            }
        </div>
    `;

    // Insert switcher after the menu title
    const menuTitle = document.querySelector('.menu-title');
    if (menuTitle && menuTitle.parentNode) {
        menuTitle.parentNode.insertAdjacentHTML('afterend', switcherHtml);
    }
})();
