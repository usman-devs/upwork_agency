// HTMX configuration
document.body.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token to all HTMX requests
    event.detail.headers['X-CSRFToken'] = document.querySelector('meta[name="csrf-token"]').content;
});

// Toast notifications for flash messages
document.addEventListener('DOMContentLoaded', () => {
    // Auto-close alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});