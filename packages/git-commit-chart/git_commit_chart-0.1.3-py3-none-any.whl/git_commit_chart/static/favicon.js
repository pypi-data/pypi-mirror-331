function updateFavicon() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // Update SVG favicon
    let svgFavicon = document.querySelector('link[rel="icon"][type="image/svg+xml"]');
    if (!svgFavicon) {
        svgFavicon = document.createElement('link');
        svgFavicon.rel = 'icon';
        svgFavicon.type = 'image/svg+xml';
        document.head.appendChild(svgFavicon);
    }
    svgFavicon.href = isDark ? '/static/favicon/favicon-dark.svg' : '/static/favicon/favicon-light.svg';

    // Ensure ICO favicon is present
    if (!document.querySelector('link[rel="alternate icon"]')) {
        const icoFavicon = document.createElement('link');
        icoFavicon.rel = 'alternate icon';
        icoFavicon.type = 'image/x-icon';
        icoFavicon.href = '/static/favicon/favicon.ico';
        document.head.appendChild(icoFavicon);
    }
}

// Update favicon when theme changes
document.addEventListener('themeChanged', updateFavicon);

// Set initial favicon
document.addEventListener('DOMContentLoaded', updateFavicon); 