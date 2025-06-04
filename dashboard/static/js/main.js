/**
 * AIA Analytics Dashboard - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile sidebar toggle
    initSidebar();
    
    // Setup tooltips
    setupTooltips();
    
    // Setup any expandable sections
    setupExpandables();
    
    // Handle any light/dark mode toggles (if implemented)
    setupThemeToggle();
});

/**
 * Initialize mobile sidebar functionality
 */
function initSidebar() {
    const menuButton = document.querySelector('.lni-menu');
    const sidebar = document.querySelector('aside');
    
    if (menuButton && sidebar) {
        menuButton.addEventListener('click', function() {
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('block');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth < 768) {
                if (!sidebar.contains(event.target) && !menuButton.contains(event.target)) {
                    sidebar.classList.add('hidden');
                    sidebar.classList.remove('block');
                }
            }
        });
    }
}

/**
 * Setup tooltips for data points
 */
function setupTooltips() {
    // This would be implemented if using a tooltip library
    // or custom tooltip functionality
    console.log('Tooltips initialized');
}

/**
 * Handle expandable/collapsible sections
 */
function setupExpandables() {
    const expandables = document.querySelectorAll('[data-expandable]');
    
    expandables.forEach(section => {
        const trigger = section.querySelector('[data-expandable-trigger]');
        const content = section.querySelector('[data-expandable-content]');
        
        if (trigger && content) {
            trigger.addEventListener('click', function() {
                content.classList.toggle('u-hidden');
                
                // Toggle icon if present
                const icon = trigger.querySelector('i');
                if (icon) {
                    if (content.classList.contains('u-hidden')) {
                        icon.classList.replace('lni-chevron-up', 'lni-chevron-down');
                    } else {
                        icon.classList.replace('lni-chevron-down', 'lni-chevron-up');
                    }
                }
            });
        }
    });
}

/**
 * Handle light/dark mode toggle
 */
function setupThemeToggle() {
    // AIA dashboard is light theme by default
    // This is a placeholder for future theme toggle functionality
    console.log('Theme system initialized');
}

/**
 * Format date in a human-readable format
 * @param {string|Date} dateString - Date to format
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format number with commas
 * @param {number} number - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Limit string length and add ellipsis
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated string
 */
function truncateString(str, maxLength = 30) {
    if (!str) return '';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

/**
 * Create and download a CSV file
 * @param {Array} data - Array of objects to convert to CSV
 * @param {string} filename - Name of the CSV file
 */
function downloadCSV(data, filename = 'export.csv') {
    if (!data || !data.length) {
        console.error('No data to export');
        return;
    }
    
    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV rows
    const csvRows = [];
    csvRows.push(headers.join(','));
    
    // Add data rows
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header] || '';
            // Escape quotes and wrap in quotes if necessary
            return `"${String(value).replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    }
    
    // Create blob and download link
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Generic data fetching utility with error handling
 * @param {string} url - API endpoint to fetch
 * @returns {Promise} - Promise resolving to JSON data
 */
async function fetchData(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        // Show error message to user
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.textContent = `Failed to load data. ${error.message}`;
            errorContainer.classList.remove('u-hidden');
        }
        return null;
    }
}

/**
 * Drill down to detailed view
 * @param {string} entityType - Type of entity (agent, conversation)
 * @param {string} id - Entity ID
 */
function drillDown(entityType, id) {
    if (!entityType || !id) return;
    
    // Navigate to detail page
    window.location.href = `/${entityType}/${id}`;
}

// Export utilities for use in other modules
window.aiaUtils = {
    formatDate,
    formatNumber,
    truncateString,
    downloadCSV,
    fetchData,
    drillDown
}; 