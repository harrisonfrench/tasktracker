// Task Tracker Pro X - Modern JavaScript Application
class TaskTrackerApp {
    constructor() {
        this.socket = null;
        this.init();
    }

    init() {
        this.initTheme();
        this.initSocketIO();
        this.initEventListeners();
        this.initAnimations();
        console.log('🚀 Task Tracker Pro X initialized successfully!');
    }

    // Theme Management
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeIcon = document.querySelector('.theme-toggle i');
        if (themeIcon) {
            themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    // Socket.IO for real-time features
    initSocketIO() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('🔌 Connected to server');
            });
            
            this.socket.on('task_updated', (data) => {
                this.handleTaskUpdate(data);
            });
            
            this.socket.on('notification', (data) => {
                this.showNotification(data.message, data.type);
            });
        }
    }

    // Event Listeners
    initEventListeners() {
        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleAjaxForm(e.target);
            }
        });

        // Modal triggers
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal-target]')) {
                const modalId = e.target.getAttribute('data-modal-target');
                this.showModal(modalId);
            }
            
            if (e.target.matches('[data-modal-close]')) {
                this.hideModal(e.target.closest('.modal'));
            }
        });

        // Task actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.task-complete-btn')) {
                this.toggleTaskComplete(e.target);
            }
            
            if (e.target.matches('.task-delete-btn')) {
                this.deleteTask(e.target);
            }
        });

        // Search functionality
        const searchInput = document.getElementById('taskSearch');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.searchTasks(e.target.value);
            }, 300));
        }

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    // Animations
    initAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.card, .stat-card').forEach(el => {
            observer.observe(el);
        });
    }

    // AJAX Form Handling
    async handleAjaxForm(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message || 'Operation successful!', 'success');
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    this.refreshPage();
                }
            } else {
                this.showNotification(data.error || 'An error occurred', 'error');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Network error occurred', 'error');
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    // Modal Management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Focus first input
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    hideModal(modal) {
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    hideAllModals() {
        document.querySelectorAll('.modal.show').forEach(modal => {
            this.hideModal(modal);
        });
    }

    // Task Management
    async toggleTaskComplete(button) {
        const taskId = button.getAttribute('data-task-id');
        const taskCard = button.closest('.task-card');
        
        try {
            const response = await fetch(`/api/tasks/${taskId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                taskCard.classList.toggle('task-completed');
                button.innerHTML = data.completed ? 
                    '<i class="fas fa-undo"></i>' : 
                    '<i class="fas fa-check"></i>';
                
                this.showNotification(data.message, 'success');
                this.updateUserStats();
            }
        } catch (error) {
            console.error('Task toggle error:', error);
            this.showNotification('Failed to update task', 'error');
        }
    }

    async deleteTask(button) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }
        
        const taskId = button.getAttribute('data-task-id');
        const taskCard = button.closest('.task-card');
        
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                taskCard.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    taskCard.remove();
                    this.showNotification('Task deleted', 'info');
                }, 300);
            }
        } catch (error) {
            console.error('Task deletion error:', error);
            this.showNotification('Failed to delete task', 'error');
        }
    }

    // Search functionality
    searchTasks(query) {
        const taskCards = document.querySelectorAll('.task-card');
        
        taskCards.forEach(card => {
            const title = card.querySelector('.task-title')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.task-description')?.textContent.toLowerCase() || '';
            const searchText = (title + ' ' + description).toLowerCase();
            
            if (searchText.includes(query.toLowerCase()) || query === '') {
                card.style.display = '';
                card.classList.add('animate-fade-in');
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Notifications
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    // Real-time updates
    handleTaskUpdate(data) {
        const taskCard = document.querySelector(`[data-task-id="${data.task_id}"]`);
        if (taskCard) {
            // Update task card with new data
            this.updateTaskCard(taskCard, data);
        }
    }

    updateTaskCard(card, data) {
        const title = card.querySelector('.task-title');
        const description = card.querySelector('.task-description');
        const priority = card.querySelector('.task-priority');
        
        if (title) title.textContent = data.title;
        if (description) description.textContent = data.description;
        if (priority) {
            priority.className = `badge task-priority badge-${data.priority}`;
            priority.textContent = data.priority.toUpperCase();
        }
    }

    // User stats update
    async updateUserStats() {
        try {
            const response = await fetch('/api/user/stats');
            const stats = await response.json();
            
            // Update stats in dashboard
            Object.entries(stats).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    element.textContent = value;
                }
            });
        } catch (error) {
            console.error('Stats update error:', error);
        }
    }

    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    refreshPage() {
        window.location.reload();
    }

    // Chart initialization (if Chart.js is available)
    initCharts() {
        if (typeof Chart !== 'undefined') {
            this.initTaskChart();
            this.initProgressChart();
        }
    }

    initTaskChart() {
        const ctx = document.getElementById('taskChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Active', 'Overdue'],
                datasets: [{
                    data: [12, 8, 3],
                    backgroundColor: ['#48bb78', '#4299e1', '#f56565'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initProgressChart() {
        const ctx = document.getElementById('progressChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Tasks Completed',
                    data: [2, 3, 1, 4, 2, 5, 3],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Global functions for template use
function toggleTheme() {
    app.toggleTheme();
}

function showNotification(message, type = 'info', duration = 5000) {
    if (window.app) {
        app.showNotification(message, type, duration);
    } else {
        // Fallback if app is not loaded yet
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.user-menu')) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TaskTrackerApp();
});

// Additional CSS for notifications
const notificationStyles = `
<style>
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 2001;
    max-width: 400px;
}

.notification-toast {
    margin-bottom: 10px;
    animation: slideInRight 0.3s ease;
}

@keyframes fadeOut {
    from { opacity: 1; transform: scale(1); }
    to { opacity: 0; transform: scale(0.8); }
}

.task-card {
    transition: all 0.3s ease;
}

.task-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.task-completed {
    opacity: 0.7;
}

.task-completed .task-title {
    text-decoration: line-through;
}

.chart-container {
    position: relative;
    height: 300px;
    margin: 20px 0;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);
