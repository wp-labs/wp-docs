// Language Switcher Script
(function() {
    // Get current language from path
    const path = window.location.pathname;
    let currentLang = 'en';
    let currentPage = '/';

    if (path.match(/^\/zh\//)) {
        currentLang = 'zh';
        currentPage = path.replace(/^\/zh\//, '/');
    } else if (path.match(/^\/en\//)) {
        currentLang = 'en';
        currentPage = path.replace(/^\/en\//, '/');
    } else {
        currentPage = path === '/' ? '/index.html' : path;
    }

    // Build language switcher HTML
    const zhUrl = '/zh' + currentPage;
    const enUrl = '/en' + currentPage;

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
