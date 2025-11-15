
// ============================================================================
// Theme Toggle with LocalStorage
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    body.classList.toggle('dark-mode', currentTheme === 'dark');
    
    if (themeToggle) {
        updateThemeToggleButton(currentTheme === 'dark');
        
        themeToggle.addEventListener('click', function() {
            const isDark = body.classList.toggle('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeToggleButton(isDark);
        });
    }
    
    function updateThemeToggleButton(isDark) {
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (isDark) {
                icon.className = 'fas fa-sun';
                themeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
            } else {
                icon.className = 'fas fa-moon';
                themeToggle.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
            }
        }
    }
});

// ============================================================================
// Auto-dismiss Alerts
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        // Add close button if not exists
        if (!alert.querySelector('.btn-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'btn-close';
            closeBtn.setAttribute('data-bs-dismiss', 'alert');
            alert.appendChild(closeBtn);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// ============================================================================
// Number Input Formatting
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
});

// ============================================================================
// Confirm Delete Actions
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-message') || 
                          'Are you sure you want to delete this? This action cannot be undone.';
            
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// ============================================================================
// Initialize Bootstrap Tooltips
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// ============================================================================
// Search/Filter Functionality
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchExpenses');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('.expense-row, tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
});

// ============================================================================
// Animated Number Counter
// ============================================================================
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = formatCurrency(end);
            clearInterval(timer);
        } else {
            element.textContent = formatCurrency(current);
        }
    }, 16);
}

function formatCurrency(value) {
    return '₦' + Math.abs(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// ============================================================================
// Progress Bar Animation
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const targetWidth = progressBar.getAttribute('data-width') || 
                                  progressBar.style.width;
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = targetWidth;
                }, 100);
                observer.unobserve(progressBar);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => observer.observe(bar));
});

// ============================================================================
// Smooth Scroll to Anchor
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// ============================================================================
// Form Validation Enhancement
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// ============================================================================
// Dynamic Budget Warning Colors
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const budgetBars = document.querySelectorAll('.progress-bar[data-budget-percentage]');
    
    budgetBars.forEach(bar => {
        const percentage = parseFloat(bar.getAttribute('data-budget-percentage'));
        
        bar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        
        if (percentage >= 100) {
            bar.classList.add('bg-danger');
        } else if (percentage >= 80) {
            bar.classList.add('bg-warning');
        } else {
            bar.classList.add('bg-success');
        }
    });
});

// ============================================================================
// Recurring Expense Toggle
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const recurringCheckbox = document.getElementById('is_recurring');
    const frequencyField = document.getElementById('recurrence_frequency');
    
    if (recurringCheckbox && frequencyField) {
        const frequencyContainer = frequencyField.closest('.mb-3') || frequencyField.parentElement;
        
        function toggleFrequency() {
            if (frequencyContainer) {
                frequencyContainer.style.display = recurringCheckbox.checked ? 'block' : 'none';
            }
        }
        
        toggleFrequency();
        recurringCheckbox.addEventListener('change', toggleFrequency);
    }
});

// ============================================================================
// Chart.js Default Configuration
// ============================================================================
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.color = '#6b7280';
    Chart.defaults.plugins.legend.labels.padding = 15;
    Chart.defaults.plugins.legend.labels.boxWidth = 15;
    Chart.defaults.plugins.legend.labels.boxHeight = 15;
}

// ============================================================================
// Utility Functions
// ============================================================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3 fade show`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(toast);
        bsAlert.close();
    }, 4000);
}

// ============================================================================
// Chart Initialization
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    const categoryChartCanvas = document.getElementById('categoryChart');
    if (categoryChartCanvas) {
        const chartDataAttr = categoryChartCanvas.getAttribute('data-chart');
        if (chartDataAttr) {
            try {
                const chartData = JSON.parse(chartDataAttr);

                // Check if we have data to display
                if (chartData.categories && chartData.categories.length > 0 &&
                    chartData.amounts && chartData.amounts.length > 0 &&
                    chartData.colors && chartData.colors.length > 0) {

                    const ctx = categoryChartCanvas.getContext('2d');

                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: chartData.categories,
                            datasets: [{
                                data: chartData.amounts,
                                backgroundColor: chartData.colors,
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'right',
                                    labels: {
                                        font: {
                                            family: "'Inter', sans-serif",
                                            size: 12
                                        }
                                    }
                                }
                            }
                        }
                    });
                } else {
                    // Show message when no data
                    const ctx = categoryChartCanvas.getContext('2d');
                    ctx.font = '16px Inter, sans-serif';
                    ctx.fillStyle = '#6b7280';
                    ctx.textAlign = 'center';
                    ctx.fillText('No expense data available', categoryChartCanvas.width / 2, categoryChartCanvas.height / 2);
                }
            } catch (e) {
                console.error('Error parsing chart data:', e);
                // Show error message on canvas
                const ctx = categoryChartCanvas.getContext('2d');
                ctx.font = '14px Inter, sans-serif';
                ctx.fillStyle = '#ef4444';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading chart', categoryChartCanvas.width / 2, categoryChartCanvas.height / 2);
            }
        }
    }
});

// ============================================================================
// Alert Dismissal
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.alert-dismiss').forEach(button => {
        button.addEventListener('click', function() {
            fetch('/budgets/mark_alerts_read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const alertsContainer = document.querySelector('.alerts-container');
                    if (alertsContainer) {
                        alertsContainer.remove();
                    }
                }
            });
        });
    });
});

// ============================================================================
// Export for use in other scripts
// ============================================================================
window.Centsible = {
    animateValue,
    formatCurrency,
    showToast,
    debounce
};


/* ============================================================================
   ADD TO base.html - Theme Toggle Button
   
   Add this in your header where you want the theme toggle:
   
   <button id="theme-toggle" class="btn btn-sm">
       <i class="fas fa-moon"></i> Dark Mode
   </button>
============================================================================ */