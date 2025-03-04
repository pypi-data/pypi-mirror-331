// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.getElementById('theme-switch').checked = savedTheme === 'dark';
    updateChartTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateChartTheme(newTheme);
}

function updateChartTheme(theme) {
    const isDark = theme === 'dark';
    const textColor = isDark ? '#e2e8f0' : '#2d3748';
    const gridColor = isDark ? '#4a5568' : '#e2e8f0';

    // Update Chart.js defaults
    Chart.defaults.color = textColor;
    Chart.defaults.borderColor = gridColor;

    // If there's an active chart, update it
    if (window.chart) {
        window.chart.options.scales.x.grid.color = gridColor;
        window.chart.options.scales.y.grid.color = gridColor;
        window.chart.options.scales.x.ticks.color = textColor;
        window.chart.options.scales.y.ticks.color = textColor;
        window.chart.update();
    }
} 