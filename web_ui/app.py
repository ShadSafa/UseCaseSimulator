"""
Main Flask application for Use Case Simulator Web UI.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_session import Session
import os
import sys
from datetime import datetime

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import get_config
from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.core.simulation_state import SimulationState
from modules.analytics.analytics_manager import AnalyticsManager


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize Flask-Session
    Session(app)

    # Initialize analytics manager
    analytics_manager = AnalyticsManager()

    # Register blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.game import game_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(game_bp, url_prefix='/game')

    # Template filters
    @app.template_filter('currency')
    def format_currency(value):
        """Format value as currency."""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return f"${value}"

    @app.template_filter('percentage')
    def format_percentage(value, decimals=1):
        """Format value as percentage."""
        try:
            return f"{float(value) * 100:.{decimals}f}%"
        except (ValueError, TypeError):
            return f"{value}"

    @app.template_filter('round_number')
    def format_round_number(value):
        """Format round number."""
        try:
            return f"Round {int(value)}"
        except (ValueError, TypeError):
            return str(value)

    # Context processors
    @app.context_processor
    def inject_now():
        """Inject current datetime into templates."""
        return {'now': datetime.utcnow()}

    @app.context_processor
    def inject_game_state():
        """Inject game state into templates."""
        game_state = session.get('game_state')
        if game_state:
            return {'game_state': SimulationState.from_dict(game_state)}
        return {'game_state': None}

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    return app


# Create the application instance
app = create_app()


# Remove the direct app.run() call - use run_web.py instead