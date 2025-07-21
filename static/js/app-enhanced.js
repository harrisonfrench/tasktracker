/**
 * Advanced Task Tracker Pro - Enhanced JavaScript Features
 * Professional-grade interactive functionality
 */

class TaskTrackerPro {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupRealTimeUpdates();
    }

    init() {
        // Initialize theme
        this.initializeTheme();
        
        // Initialize notification system
        this.initializeNotifications();
        
        // Initialize keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Initialize charts
        this.initializeCharts();
        
        // Initialize drag and drop
        this.initializeDragDrop();
        
        console.log('🚀 Task Tracker Pro Enhanced - Initialized');
    }

    // Theme Management
    initializeTheme() {
        const savedTheme = localStorage.getItem('tasktracker-theme') || 'light';
        this.setTheme(savedTheme);
        
        // Auto theme detection
        if (savedTheme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.setTheme(prefersDark ? 'dark' : 'light');
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('tasktracker-theme', theme);
        
        // Update theme toggle button
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.querySelector('i').className = 
                theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('tasktracker-theme', newTheme);
        
        // Update theme icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.setAttribute('data-lucide', newTheme === 'dark' ? 'sun' : 'moon');
            // Re-initialize lucide icons
            if (window.lucide) {
                try {
                    setTimeout(() => window.lucide.createIcons(), 100);
                } catch (error) {
                    console.warn('Error re-initializing icons after theme change:', error);
                }
            }
        }
        
        // Animate the transition
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    // Real-time Updates
    setupRealTimeUpdates() {
        // Simulate real-time updates (in production, use WebSockets)
        setInterval(() => {
            this.updateNotificationBadge();
            this.updateDashboardStats();
        }, 30000); // Update every 30 seconds
    }

    async updateNotificationBadge() {
        try {
            const response = await fetch('/api/notifications?limit=1');
            const data = await response.json();
            
            if (data.status === 'success') {
                const badge = document.querySelector('.notification-badge');
                if (badge && data.unread_count > 0) {
                    badge.textContent = data.unread_count;
                    badge.style.display = 'block';
                    badge.classList.add('pulse');
                } else if (badge) {
                    badge.style.display = 'none';
                }
            }
        } catch (error) {
            console.warn('Failed to update notification badge:', error);
        }
    }

    // Advanced Search
    initializeAdvancedSearch() {
        const searchInput = document.querySelector('#advanced-search');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performAdvancedSearch(e.target.value);
            }, 300);
        });
    }

    async performAdvancedSearch(query) {
        if (query.length < 2) return;

        try {
            const response = await fetch(`/api/tasks/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displaySearchResults(data.tasks);
            }
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    displaySearchResults(tasks) {
        const resultsContainer = document.querySelector('#search-results');
        if (!resultsContainer) return;

        resultsContainer.innerHTML = tasks.map(task => `
            <div class="search-result-item" onclick="window.location.href='/tasks/${task.id}'">
                <div class="search-result-title">${task.title}</div>
                <div class="search-result-meta">
                    <span class="project-name">${task.project?.name || 'No Project'}</span>
                    <span class="priority priority-${task.priority}">${task.priority}</span>
                </div>
            </div>
        `).join('');

        resultsContainer.style.display = tasks.length > 0 ? 'block' : 'none';
    }

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Quick search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openQuickSearch();
            }
            
            // Ctrl/Cmd + N: New task
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.openNewTaskModal();
            }
            
            // Ctrl/Cmd + D: Dashboard
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                window.location.href = '/dashboard';
            }
            
            // T: Toggle theme
            if (e.key === 't' && !e.target.matches('input, textarea')) {
                this.toggleTheme();
            }
        });
    }

    openQuickSearch() {
        const searchModal = document.querySelector('#quick-search-modal');
        if (searchModal) {
            searchModal.style.display = 'flex';
            searchModal.querySelector('input').focus();
        }
    }

    openNewTaskModal() {
        const modal = document.querySelector('#new-task-modal');
        if (modal) {
            modal.style.display = 'flex';
            modal.querySelector('input[name="title"]').focus();
        }
    }

    // Charts and Analytics
    initializeCharts() {
        this.initializeProductivityChart();
        this.initializeProjectChart();
        this.initializePriorityChart();
    }

    async initializeProductivityChart() {
        const chartContainer = document.querySelector('#productivity-chart');
        if (!chartContainer) return;

        try {
            const response = await fetch('/api/analytics/productivity?days=30');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderProductivityChart(chartContainer, data.data);
            }
        } catch (error) {
            console.error('Failed to load productivity chart:', error);
        }
    }

    renderProductivityChart(container, data) {
        // Create a simple chart using CSS and JavaScript
        const dailyData = data.daily_productivity || [];
        
        container.innerHTML = `
            <div class="chart-header">
                <h4>30-Day Productivity Trend</h4>
            </div>
            <div class="chart-bars">
                ${dailyData.slice(-7).map(day => `
                    <div class="chart-bar-container">
                        <div class="chart-bar" style="height: ${Math.max(day.tasks_completed * 10, 5)}px">
                            <div class="bar-value">${day.tasks_completed}</div>
                        </div>
                        <div class="bar-label">${new Date(day.date).toLocaleDateString('en', {weekday: 'short'})}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Drag and Drop for Tasks
    initializeDragDrop() {
        const taskLists = document.querySelectorAll('.task-list');
        
        taskLists.forEach(list => {
            list.addEventListener('dragover', this.handleDragOver);
            list.addEventListener('drop', this.handleDrop.bind(this));
        });

        const taskItems = document.querySelectorAll('.task-item');
        taskItems.forEach(item => {
            item.draggable = true;
            item.addEventListener('dragstart', this.handleDragStart);
        });
    }

    handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.taskId);
        e.target.classList.add('dragging');
    }

    handleDragOver(e) {
        e.preventDefault();
    }

    async handleDrop(e) {
        e.preventDefault();
        
        const taskId = e.dataTransfer.getData('text/plain');
        const newStatus = e.currentTarget.dataset.status;
        
        if (taskId && newStatus) {
            await this.updateTaskStatus(taskId, newStatus);
        }

        // Remove dragging class
        document.querySelectorAll('.dragging').forEach(el => {
            el.classList.remove('dragging');
        });
    }

    async updateTaskStatus(taskId, newStatus) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (response.ok) {
                this.showNotification('Task updated successfully!', 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (error) {
            console.error('Failed to update task:', error);
            this.showNotification('Failed to update task', 'error');
        }
    }

    // Notification System
    initializeNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('#notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('#notification-container');
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);

        // Add entrance animation
        setTimeout(() => notification.classList.add('notification-show'), 10);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Time Tracking
    async startTimeTracking(taskId) {
        try {
            const response = await fetch('/api/time-tracking/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(`Started tracking time for "${data.task_title}"`, 'success');
                this.updateTimeTrackingUI(true, data.time_log_id);
            }
        } catch (error) {
            console.error('Failed to start time tracking:', error);
        }
    }

    async stopTimeTracking() {
        try {
            const response = await fetch('/api/time-tracking/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(`Tracked ${data.duration_hours} hours`, 'success');
                this.updateTimeTrackingUI(false);
            }
        } catch (error) {
            console.error('Failed to stop time tracking:', error);
        }
    }

    updateTimeTrackingUI(isTracking, timeLogId = null) {
        const trackingBtn = document.querySelector('#time-tracking-btn');
        if (trackingBtn) {
            trackingBtn.textContent = isTracking ? 'Stop Tracking' : 'Start Tracking';
            trackingBtn.className = isTracking ? 'btn btn-danger' : 'btn btn-success';
            trackingBtn.dataset.timeLogId = timeLogId || '';
        }
    }

    // Event Listeners
    setupEventListeners() {
        // Theme toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('.theme-toggle') || e.target.closest('.theme-toggle')) {
                this.toggleTheme();
            }
        });

        // Quick actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="quick-complete"]')) {
                this.quickCompleteTask(e.target.dataset.taskId);
            }
        });

        // Advanced search initialization
        this.initializeAdvancedSearch();
    }

    async quickCompleteTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'completed' })
            });

            if (response.ok) {
                this.showNotification('Task completed! 🎉', 'success');
                
                // Add completion animation
                const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskElement) {
                    taskElement.classList.add('task-completed');
                    setTimeout(() => taskElement.remove(), 1000);
                }
            }
        } catch (error) {
            console.error('Failed to complete task:', error);
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard/widgets');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateDashboardWidgets(data.widgets);
            }
        } catch (error) {
            console.warn('Failed to load dashboard data:', error);
        }
    }

    updateDashboardWidgets(widgets) {
        // Update quick stats
        if (widgets.quick_stats) {
            const stats = widgets.quick_stats;
            this.updateElement('#total-tasks-count', stats.total_tasks);
            this.updateElement('#completed-tasks-count', stats.completed_tasks);
            this.updateElement('#completion-rate', `${stats.completion_rate}%`);
            this.updateElement('#active-projects-count', stats.active_projects);
        }

        // Update recent activity
        if (widgets.recent_activity) {
            this.updateRecentActivity(widgets.recent_activity);
        }

        // Update upcoming deadlines
        if (widgets.upcoming_deadlines) {
            this.updateUpcomingDeadlines(widgets.upcoming_deadlines);
        }
    }

    updateElement(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    }

    updateRecentActivity(activities) {
        const container = document.querySelector('#recent-activity-list');
        if (!container || !activities.length) return;

        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-${activity.status === 'completed' ? 'check' : 'edit'}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-meta">${activity.project_name} • ${this.formatDate(activity.updated_at)}</div>
                </div>
            </div>
        `).join('');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
        
        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffHours < 48) return 'Yesterday';
        return date.toLocaleDateString();
    }
}

// Navigation Functions
function toggleNotifications() {
    const menu = document.getElementById('notifications-menu');
    if (!menu) {
        console.warn('Notifications menu not found');
        return;
    }
    
    const isVisible = menu.style.display !== 'none';
    
    // Close other dropdowns
    closeAllDropdowns();
    
    if (!isVisible) {
        menu.style.display = 'block';
        loadNotifications();
    }
}

function toggleProfileMenu() {
    const menu = document.getElementById('profile-menu');
    const dropdown = document.querySelector('.profile-dropdown');
    
    if (!menu) {
        console.warn('Profile menu not found');
        return;
    }
    
    const isVisible = menu.style.display !== 'none';
    
    // Close other dropdowns
    closeAllDropdowns();
    
    if (!isVisible) {
        menu.style.display = 'block';
        if (dropdown) {
            dropdown.classList.add('open');
        }
    } else if (dropdown) {
        dropdown.classList.remove('open');
    }
}

function toggleUserMenu() {
    // Legacy function - redirect to profile menu
    toggleProfileMenu();
}

function closeAllDropdowns() {
    const dropdowns = [
        'notifications-menu',
        'profile-menu'
    ];
    
    dropdowns.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Remove open class from profile dropdown
    const profileDropdown = document.querySelector('.profile-dropdown');
    if (profileDropdown) {
        profileDropdown.classList.remove('open');
    }
}

function showPreferences() {
    // Placeholder for preferences modal
    showToast('Preferences feature coming soon!', 'info');
}

function loadNotifications() {
    const notificationsList = document.getElementById('notifications-list');
    const notificationCount = document.getElementById('notification-count');
    
    // Check if elements exist before proceeding
    if (!notificationsList || !notificationCount) {
        console.warn('Notification elements not found, skipping load');
        return;
    }
    
    // Fetch notifications from API
    fetch('/api/notifications')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                notificationsList.innerHTML = data.notifications.map(notification => `
                    <div class="notification-item ${notification.read ? '' : 'unread'}">
                        <div class="notification-content">
                            <div class="notification-title">${notification.title}</div>
                            <div class="notification-message">${notification.message}</div>
                            <div class="notification-time">${formatTime(notification.created_at)}</div>
                        </div>
                        ${!notification.read ? '<div class="notification-dot"></div>' : ''}
                    </div>
                `).join('');
                
                const unreadCount = data.notifications.filter(n => !n.read).length;
                if (unreadCount > 0) {
                    notificationCount.textContent = unreadCount;
                    notificationCount.style.display = 'block';
                } else {
                    notificationCount.style.display = 'none';
                }
            } else {
                notificationsList.innerHTML = '<div class="no-notifications">No new notifications</div>';
                notificationCount.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            if (notificationsList) {
                notificationsList.innerHTML = '<div class="no-notifications">Error loading notifications</div>';
            }
            if (notificationCount) {
                notificationCount.style.display = 'none';
            }
        });
}

function markAllNotificationsRead() {
    fetch('/api/notifications/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadNotifications();
            showToast('All notifications marked as read', 'success');
        }
    })
    .catch(error => {
        console.error('Error marking notifications as read:', error);
    });
}

function openQuickTaskModal() {
    // Create quick task modal if it doesn't exist
    let modal = document.getElementById('quick-task-modal');
    if (!modal) {
        modal = createQuickTaskModal();
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
}

function createQuickTaskModal() {
    const modal = document.createElement('div');
    modal.id = 'quick-task-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Quick Task</h3>
                <button class="modal-close" onclick="closeQuickTaskModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="quick-task-form">
                    <div class="form-group">
                        <label for="quick-task-title">Task Title</label>
                        <input type="text" id="quick-task-title" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="quick-task-priority">Priority</label>
                        <select id="quick-task-priority" name="priority">
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="button" onclick="closeQuickTaskModal()" class="btn btn-secondary">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Task</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Add form submission handler
    modal.querySelector('#quick-task-form').addEventListener('submit', handleQuickTaskSubmit);
    
    return modal;
}

function closeQuickTaskModal() {
    const modal = document.getElementById('quick-task-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.querySelector('#quick-task-form').reset();
    }
}

function handleQuickTaskSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const taskData = {
        title: formData.get('title'),
        priority: formData.get('priority'),
        status: 'todo'
    };
    
    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Task created successfully!', 'success');
            closeQuickTaskModal();
            // Refresh page or update UI
            if (window.location.pathname.includes('tasks') || window.location.pathname === '/') {
                location.reload();
            }
        } else {
            showToast('Error creating task', 'error');
        }
    })
    .catch(error => {
        console.error('Error creating task:', error);
        showToast('Error creating task', 'error');
    });
}

// Global search functionality
function setupGlobalSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performGlobalSearch(query);
                }, 300);
            } else {
                hideSearchResults();
            }
        });
        
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query) {
                    window.location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        });
    }
}

function performGlobalSearch(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    let searchResults = document.getElementById('search-results');
    if (!searchResults) {
        searchResults = document.createElement('div');
        searchResults.id = 'search-results';
        searchResults.className = 'search-results-dropdown';
        const searchContainer = document.querySelector('.quick-search');
        if (searchContainer) {
            searchContainer.appendChild(searchResults);
        }
    }
    
    if (results && results.length > 0) {
        searchResults.innerHTML = results.map(result => `
            <a href="${result.url}" class="search-result-item">
                <div class="search-result-type">${result.type}</div>
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-description">${result.description}</div>
            </a>
        `).join('');
        searchResults.style.display = 'block';
    } else {
        searchResults.innerHTML = '<div class="no-search-results">No results found</div>';
        searchResults.style.display = 'block';
    }
}

function hideSearchResults() {
    const searchResults = document.getElementById('search-results');
    if (searchResults) {
        searchResults.style.display = 'none';
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.notifications-dropdown') && 
        !e.target.closest('.profile-dropdown')) {
        closeAllDropdowns();
    }
});

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupGlobalSearch();
    loadNotifications();
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.taskTrackerPro = new TaskTrackerPro();
});

// Export for global access
window.TaskTrackerPro = TaskTrackerPro;

// Utility Functions
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('tasktracker-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.setAttribute('data-lucide', savedTheme === 'dark' ? 'sun' : 'moon');
    }
});

// Standalone theme toggle function for navbar
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('tasktracker-theme', newTheme);
    
    // Update theme icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.setAttribute('data-lucide', newTheme === 'dark' ? 'sun' : 'moon');
        // Re-initialize lucide icons
        if (window.lucide) {
            try {
                setTimeout(() => window.lucide.createIcons(), 100);
            } catch (error) {
                console.warn('Error re-initializing icons after theme change:', error);
            }
        }
    }
}
