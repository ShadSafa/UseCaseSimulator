/**
 * Use Case Simulator - Main JavaScript Application
 * Handles UI interactions, AJAX requests, and real-time updates
 */

class UseCaseSimulator {
    constructor() {
        this.api = new API();
        this.ui = new UI();
        this.charts = new ChartManager();
        this.session = new SessionManager();
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;

        try {
            // Initialize components
            this.ui.initialize();
            this.setupEventListeners();
            this.setupPeriodicUpdates();

            // Load initial state
            await this.loadApplicationState();

            this.initialized = true;
            console.log('Use Case Simulator initialized successfully');
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.ui.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    setupEventListeners() {
        // Form submissions
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Button clicks
        document.addEventListener('click', (e) => this.handleButtonClick(e));

        // Navigation
        window.addEventListener('popstate', (e) => this.handleNavigation(e));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    setupPeriodicUpdates() {
        // Update game state every 30 seconds if game is active
        setInterval(() => {
            if (this.session.hasActiveGame()) {
                this.updateGameState();
            }
        }, 30000);

        // Update analytics every 60 seconds
        setInterval(() => {
            if (this.session.hasActiveGame()) {
                this.updateAnalytics();
            }
        }, 60000);
    }

    async loadApplicationState() {
        try {
            // Check if there's an active game
            const gameState = await this.api.get('/api/game/state');
            if (gameState && gameState.success) {
                this.session.setGameState(gameState.data);
                this.ui.updateDashboard(gameState.data);
            }
        } catch (error) {
            console.log('No active game session found');
        }
    }

    async handleFormSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const action = form.dataset.action;

        try {
            this.ui.showLoading(form);

            let response;
            switch (action) {
                case 'new-game':
                    response = await this.createNewGame(formData);
                    break;
                case 'load-game':
                    response = await this.loadGame(formData);
                    break;
                case 'decisions':
                    response = await this.submitDecisions(formData);
                    break;
                case 'save-game':
                    response = await this.saveGame(formData);
                    break;
                default:
                    throw new Error('Unknown form action');
            }

            if (response.success) {
                this.ui.showSuccess(response.message || 'Action completed successfully');
                if (response.redirect) {
                    window.location.href = response.redirect;
                }
            } else {
                throw new Error(response.message || 'Action failed');
            }

        } catch (error) {
            console.error('Form submission error:', error);
            this.ui.showError(error.message || 'An error occurred');
        } finally {
            this.ui.hideLoading(form);
        }
    }

    async handleButtonClick(event) {
        const button = event.target.closest('button[data-action]');
        if (!button) return;

        const action = button.dataset.action;
        const data = button.dataset;

        try {
            this.ui.showLoading(button);

            let response;
            switch (action) {
                case 'end-round':
                    response = await this.endRound();
                    break;
                case 'new-round':
                    response = await this.startNewRound();
                    break;
                case 'quit-game':
                    if (confirm('Are you sure you want to quit? Unsaved progress will be lost.')) {
                        response = await this.quitGame();
                    }
                    break;
                default:
                    return;
            }

            if (response && response.success) {
                this.ui.showSuccess(response.message || 'Action completed');
                if (response.redirect) {
                    window.location.href = response.redirect;
                }
            }

        } catch (error) {
            console.error('Button action error:', error);
            this.ui.showError(error.message || 'Action failed');
        } finally {
            this.ui.hideLoading(button);
        }
    }

    async createNewGame(formData) {
        const gameData = {
            company_name: formData.get('company_name') || 'My Company',
            difficulty: formData.get('difficulty') || 'medium',
            scenario: formData.get('scenario') || 'default'
        };

        const response = await this.api.post('/api/game/new', gameData);
        if (response.success) {
            this.session.setGameState(response.data);
        }
        return response;
    }

    async loadGame(formData) {
        const saveName = formData.get('save_name');
        if (!saveName) {
            throw new Error('Please select a save file');
        }

        const response = await this.api.post('/api/game/load', { save_name: saveName });
        if (response.success) {
            this.session.setGameState(response.data);
        }
        return response;
    }

    async submitDecisions(formData) {
        const decisions = {
            pricing: formData.get('pricing') ? { price: parseFloat(formData.get('pricing')) } : null,
            marketing: formData.get('marketing') ? { budget: parseFloat(formData.get('marketing')) } : null,
            capacity_expansion: formData.get('capacity_expansion') ? { expansion_amount: parseFloat(formData.get('capacity_expansion')) } : null,
            quality_improvement: formData.get('quality_improvement') ? { investment: parseFloat(formData.get('quality_improvement')) } : null,
            hiring: formData.get('hiring') ? { num_employees: parseInt(formData.get('hiring')) } : null,
            equipment_purchase: formData.get('equipment_purchase') ? { equipment_value: parseFloat(formData.get('equipment_purchase')) } : null
        };

        // Remove null values
        Object.keys(decisions).forEach(key => {
            if (!decisions[key]) delete decisions[key];
        });

        const response = await this.api.post('/api/game/decision', { decisions });
        if (response.success) {
            this.session.updateGameState(response.data);
            this.ui.updateRoundResults(response.data);
        }
        return response;
    }

    async saveGame(formData) {
        const saveName = formData.get('save_name') || `save_${Date.now()}`;
        return await this.api.post('/api/game/save', { save_name: saveName });
    }

    async endRound() {
        // This would trigger the round calculation
        return await this.api.post('/api/game/end-round');
    }

    async startNewRound() {
        const response = await this.api.post('/api/game/new-round');
        if (response.success) {
            this.session.updateGameState(response.data);
            this.ui.updateDashboard(response.data);
        }
        return response;
    }

    async quitGame() {
        this.session.clearGameState();
        return { success: true, redirect: '/' };
    }

    async updateGameState() {
        try {
            const response = await this.api.get('/api/game/state');
            if (response.success) {
                this.session.setGameState(response.data);
                this.ui.updateDashboard(response.data);
            }
        } catch (error) {
            console.log('Failed to update game state:', error);
        }
    }

    async updateAnalytics() {
        try {
            const response = await this.api.get('/api/analytics/kpis');
            if (response.success) {
                this.ui.updateAnalytics(response.data);
                this.charts.updateCharts(response.data);
            }
        } catch (error) {
            console.log('Failed to update analytics:', error);
        }
    }

    handleNavigation(event) {
        // Handle browser back/forward buttons
        if (event.state) {
            this.loadApplicationState();
        }
    }

    handleKeyboard(event) {
        // Keyboard shortcuts
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 's':
                    event.preventDefault();
                    // Quick save
                    this.saveGame(new FormData());
                    break;
                case 'n':
                    event.preventDefault();
                    // New game
                    window.location.href = '/new-game';
                    break;
            }
        }

        // Escape key
        if (event.key === 'Escape') {
            // Close modals, cancel forms, etc.
            this.ui.closeModals();
        }
    }
}

// API Communication Class
class API {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async get(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`);
        return await response.json();
    }

    async post(endpoint, data) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    }
}

// UI Management Class
class UI {
    constructor() {
        this.loadingElements = new Set();
    }

    initialize() {
        this.setupFlashMessages();
        this.setupResponsiveMenu();
    }

    showLoading(element) {
        if (element) {
            element.classList.add('loading');
            element.innerHTML = '<div class="spinner"></div>' + element.innerHTML;
            this.loadingElements.add(element);
        }
    }

    hideLoading(element) {
        if (element) {
            element.classList.remove('loading');
            const spinner = element.querySelector('.spinner');
            if (spinner) spinner.remove();
            this.loadingElements.delete(element);
        }
    }

    showSuccess(message) {
        this.showFlashMessage(message, 'success');
    }

    showError(message) {
        this.showFlashMessage(message, 'error');
    }

    showFlashMessage(message, type = 'info') {
        const flashContainer = document.getElementById('flash-messages');
        if (!flashContainer) return;

        const flashMessage = document.createElement('div');
        flashMessage.className = `flash-message flash-${type}`;
        flashMessage.textContent = message;

        flashContainer.appendChild(flashMessage);

        // Auto-remove after 2 seconds
        setTimeout(() => {
            flashMessage.remove();
        }, 2000);
    }

    updateDashboard(gameState) {
        // Update dashboard elements with new game state
        this.updateKPIValues(gameState);
        this.updateCompanyInfo(gameState);
        this.updateMarketInfo(gameState);
    }

    updateKPIValues(gameState) {
        if (!gameState.kpis) return;

        // Update KPI display elements
        Object.entries(gameState.kpis).forEach(([key, value]) => {
            const element = document.getElementById(`kpi-${key}`);
            if (element) {
                if (typeof value === 'number') {
                    if (key.includes('margin') || key.includes('rate') || key.includes('share')) {
                        element.textContent = `${(value * 100).toFixed(1)}%`;
                    } else if (key.includes('revenue') || key.includes('costs') || key.includes('profit')) {
                        element.textContent = `$${value.toLocaleString()}`;
                    } else {
                        element.textContent = value.toFixed(2);
                    }
                } else {
                    element.textContent = value;
                }
            }
        });
    }

    updateCompanyInfo(gameState) {
        const company = gameState.player_company;
        if (!company) return;

        // Update company name, round, etc.
        const nameElement = document.getElementById('company-name');
        if (nameElement) nameElement.textContent = company.name;

        const roundElement = document.getElementById('round-number');
        if (roundElement) roundElement.textContent = gameState.round_number;
    }

    updateMarketInfo(gameState) {
        // Update market information display
        // Implementation depends on specific UI elements
    }

    updateRoundResults(results) {
        // Update round results display
        const resultsContainer = document.getElementById('round-results');
        if (resultsContainer && results.round_results) {
            // Update results display
            this.updateKPIValues({ kpis: results.round_results });
        }
    }

    updateAnalytics(analyticsData) {
        // Update analytics displays
        // Implementation depends on analytics UI
    }

    setupFlashMessages() {
        // Auto-remove flash messages after animation
        document.addEventListener('animationend', (e) => {
            if (e.target.classList.contains('flash-message')) {
                e.target.remove();
            }
        });
    }

    setupResponsiveMenu() {
        // Mobile menu toggle
        const menuToggle = document.getElementById('menu-toggle');
        const navMenu = document.querySelector('.nav-menu');

        if (menuToggle && navMenu) {
            menuToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
    }

    closeModals() {
        // Close any open modals
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => modal.classList.remove('active'));
    }
}

// Chart Management Class
class ChartManager {
    constructor() {
        this.charts = new Map();
    }

    updateCharts(data) {
        // Update existing charts with new data
        this.charts.forEach((chart, id) => {
            if (chart.update) {
                chart.update(data);
            }
        });
    }

    destroyChart(id) {
        if (this.charts.has(id)) {
            const chart = this.charts.get(id);
            if (chart.destroy) {
                chart.destroy();
            }
            this.charts.delete(id);
        }
    }

    destroyAllCharts() {
        this.charts.forEach((chart, id) => this.destroyChart(id));
    }
}

// Session Management Class
class SessionManager {
    constructor() {
        this.gameState = null;
    }

    hasActiveGame() {
        return this.gameState !== null;
    }

    getGameState() {
        return this.gameState;
    }

    setGameState(state) {
        this.gameState = state;
    }

    updateGameState(updates) {
        if (this.gameState) {
            Object.assign(this.gameState, updates);
        }
    }

    clearGameState() {
        this.gameState = null;
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new UseCaseSimulator();
    window.UseCaseSimulator = app; // Make globally available
    app.initialize();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UseCaseSimulator, API, UI, ChartManager, SessionManager };
}