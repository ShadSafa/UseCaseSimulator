# Web UI Architecture Design for Use Case Simulator

## Overview

This document outlines the architecture for a web-based user interface for the Use Case Simulator, extending the existing console application with a modern web frontend.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask Server  │    │  Core Engine    │
│                 │    │                 │    │                 │
│  ┌────────────┐ │    │  ┌────────────┐ │    │  ┌────────────┐ │
│  │   HTML/CSS │◄┼────┼─►│   Routes   │◄┼────┼─►│ Simulation │ │
│  │            │ │    │  │            │ │    │  │   Engine   │ │
│  │ JavaScript │ │    │  │ REST API   │ │    │  └────────────┘ │
│  │   Charts   │ │    │  │            │ │    │                 │
│  └────────────┘ │    │  └────────────┘ │    │  ┌────────────┐ │
│                 │    │                 │    │  │ Analytics  │ │
│  ┌────────────┐ │    │  ┌────────────┐ │    │  │   Engine   │ │
│  │   Session  │◄┼────┼─►│   Session  │◄┼────┼─►│            │ │
│  │ Management │ │    │  │ Management │ │    │  └────────────┘ │
│  └────────────┘ │    │  └────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Backend (Flask)
- **Flask**: Lightweight web framework
- **Flask-Session**: Server-side session management
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: WSGI utility library

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with Flexbox/Grid
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Data visualization
- **Fetch API**: AJAX communication

### Data Flow
- **JSON**: API communication format
- **Sessions**: Server-side game state management
- **WebSockets** (Future): Real-time updates

## Component Architecture

### 1. Flask Application Structure

```
web_ui/
├── __init__.py
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── routes/
│   ├── __init__.py
│   ├── main.py           # Main routes (dashboard, menu)
│   ├── api.py            # REST API endpoints
│   └── game.py           # Game-specific routes
├── static/
│   ├── css/
│   │   ├── main.css      # Main stylesheet
│   │   ├── dashboard.css # Dashboard styles
│   │   └── forms.css     # Form styles
│   ├── js/
│   │   ├── app.js        # Main JavaScript
│   │   ├── charts.js     # Chart functionality
│   │   ├── forms.js      # Form handling
│   │   └── api.js        # API communication
│   └── img/              # Static images
├── templates/
│   ├── base.html         # Base template
│   ├── dashboard.html    # Main dashboard
│   ├── decisions.html    # Decision input forms
│   ├── analytics.html    # Analytics display
│   ├── results.html      # Round results
│   └── game_over.html    # End game screen
└── utils/
    ├── __init__.py
    ├── session_manager.py # Session handling
    └── template_filters.py # Jinja2 filters
```

### 2. Session Management

#### Server-Side Sessions
- **Session Storage**: Server-side session storage
- **Game State**: Complete simulation state in session
- **Security**: Session encryption and validation
- **Persistence**: Automatic saving to disk

#### Client-Side State
- **Local Storage**: User preferences and settings
- **Session Storage**: Temporary UI state
- **Cookies**: Authentication tokens (future feature)

### 3. API Design

#### REST Endpoints

```
GET  /api/game/state          # Get current game state
POST /api/game/new            # Start new game
POST /api/game/decision       # Submit round decisions
GET  /api/game/results        # Get round results
POST /api/game/save           # Save game
POST /api/game/load           # Load game
GET  /api/analytics/kpis      # Get KPI data
GET  /api/analytics/charts    # Get chart data
GET  /api/market/competitors  # Get competitor data
```

#### Response Format
```json
{
  "success": true,
  "data": {
    "game_state": {...},
    "kpis": {...},
    "charts": {...}
  },
  "message": "Operation successful"
}
```

### 4. Frontend Architecture

#### Component Structure
```html
<!-- Main Dashboard -->
<div class="dashboard">
  <header class="dashboard-header">
    <h1>Use Case Simulator</h1>
    <div class="game-info">
      <span>Round: <span id="round-number">1</span></span>
      <span>Company: <span id="company-name">My Company</span></span>
    </div>
  </header>

  <main class="dashboard-main">
    <section class="kpi-grid">
      <!-- KPI Cards -->
    </section>

    <section class="charts-section">
      <!-- Interactive Charts -->
    </section>

    <section class="decisions-section">
      <!-- Decision Forms -->
    </section>
  </main>
</div>
```

#### JavaScript Modules
```javascript
// app.js - Main application logic
class UseCaseSimulator {
  constructor() {
    this.api = new API();
    this.charts = new ChartManager();
    this.forms = new FormManager();
    this.session = new SessionManager();
  }

  async initialize() {
    await this.loadGameState();
    this.setupEventListeners();
    this.renderDashboard();
  }
}

// API communication
class API {
  async get(endpoint) {
    const response = await fetch(`/api${endpoint}`);
    return response.json();
  }

  async post(endpoint, data) {
    const response = await fetch(`/api${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

### 5. Responsive Design

#### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

#### Layout Strategy
```css
/* Mobile-first approach */
.dashboard {
  display: flex;
  flex-direction: column;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard {
    flex-direction: row;
  }

  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### 6. Chart Integration

#### Chart.js Implementation
```javascript
class ChartManager {
  constructor() {
    this.charts = new Map();
  }

  createKPITrendChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.rounds,
        datasets: [{
          label: 'Revenue',
          data: data.revenue,
          borderColor: '#2E86AB',
          backgroundColor: 'rgba(46, 134, 171, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Revenue Trend'
          }
        }
      }
    });
  }
}
```

### 7. Security Considerations

#### Session Security
- **Secure Cookies**: HttpOnly, Secure, SameSite flags
- **Session Timeout**: Automatic logout after inactivity
- **CSRF Protection**: Token-based protection
- **Input Validation**: Server-side validation of all inputs

#### Data Protection
- **Encryption**: Sensitive data encryption
- **Sanitization**: Input sanitization and validation
- **Rate Limiting**: API rate limiting
- **Audit Logging**: Security event logging

### 8. Performance Optimization

#### Frontend Optimization
- **Code Splitting**: Lazy loading of JavaScript modules
- **Asset Optimization**: Minification and compression
- **Caching**: Browser caching strategies
- **Progressive Loading**: Critical content first

#### Backend Optimization
- **Database Connection Pooling**: Efficient database access
- **Caching**: Redis/memcached for session data
- **Async Processing**: Non-blocking operations
- **CDN**: Static asset delivery

### 9. Testing Strategy

#### Unit Tests
- **Component Testing**: Individual UI components
- **API Testing**: Endpoint functionality
- **Integration Testing**: Full user workflows

#### E2E Tests
- **User Journeys**: Complete game scenarios
- **Cross-browser Testing**: Multiple browser support
- **Performance Testing**: Load and stress testing

### 10. Deployment Architecture

#### Development Environment
```
Local Development
├── Flask dev server
├── Hot reload
├── Debug mode
└── Local database
```

#### Production Environment
```
Production Deployment
├── Gunicorn WSGI server
├── Nginx reverse proxy
├── SSL/TLS encryption
├── Database clustering
└── CDN for assets
```

#### Docker Containerization
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web_ui.app:app"]
```

## Implementation Phases

### Phase 1: Core Infrastructure (T10-001 to T10-003)
- Flask application setup
- Basic routing and templates
- Dashboard skeleton

### Phase 2: User Interface (T10-004 to T10-006)
- Decision input forms
- Analytics display
- Interactive charts

### Phase 3: Advanced Features (T10-007 to T10-010)
- Session management
- Responsive design
- REST API
- Web-based save/load

## Migration Strategy

### From Console to Web
1. **Preserve Core Logic**: Keep existing simulation engine unchanged
2. **Create Web Adapters**: Wrap console UI with web interface
3. **Gradual Migration**: Implement features incrementally
4. **Dual Interface**: Support both console and web interfaces

### Data Compatibility
- **Session Format**: Convert console state to web sessions
- **Save Files**: Maintain backward compatibility
- **Analytics Data**: Unified data format for both interfaces

This architecture provides a solid foundation for a modern web-based business simulation game while maintaining compatibility with the existing console application.