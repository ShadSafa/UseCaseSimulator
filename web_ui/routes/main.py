"""
Main routes for the Use Case Simulator web application.
Handles dashboard, menu, and general pages.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from ..utils.session_manager import get_game_state, set_game_state, clear_game_state

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirects to dashboard if game is active, otherwise to menu."""
    if get_game_state():
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.menu'))


@main_bp.route('/menu')
def menu():
    """Main menu page."""
    return render_template('menu.html')


@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard page."""
    game_state = get_game_state()
    if not game_state:
        flash('No active game. Please start a new simulation.', 'warning')
        return redirect(url_for('main.menu'))

    return render_template('dashboard.html', game_state=game_state)


@main_bp.route('/new-game', methods=['GET', 'POST'])
def new_game():
    """Start a new game page."""
    if request.method == 'POST':
        # Clear any existing game
        clear_game_state()

        # Get form data
        company_name = request.form.get('company_name', 'My Company')
        difficulty = request.form.get('difficulty', 'medium')
        scenario = request.form.get('scenario', 'default')

        # Store initial game setup in session
        session['game_setup'] = {
            'company_name': company_name,
            'difficulty': difficulty,
            'scenario': scenario
        }

        flash(f'New simulation setup complete! Starting as {company_name}', 'success')
        return redirect(url_for('game.initialize_game'))

    return render_template('new_game.html')


@main_bp.route('/load-game', methods=['GET', 'POST'])
def load_game():
    """Load game page."""
    if request.method == 'POST':
        save_name = request.form.get('save_name')
        if save_name:
            # Store load request in session
            session['load_request'] = save_name
            return redirect(url_for('game.load_game'))

    # Get list of available saves
    import os
    saves_dir = os.path.join(os.getcwd(), 'data', 'saves')
    saves = []
    if os.path.exists(saves_dir):
        for f in os.listdir(saves_dir):
            if f.endswith('.json'):
                save_name = f.replace('.json', '')
                file_path = os.path.join(saves_dir, f)
                mod_time = os.path.getmtime(file_path)
                saves.append({
                    'name': save_name,
                    'filename': f,
                    'modified': mod_time
                })

    # Sort by modification time (newest first)
    saves.sort(key=lambda x: x['modified'], reverse=True)

    return render_template('load_game.html', saves=saves)


@main_bp.route('/help')
def help():
    """Help and tutorial page."""
    return render_template('help.html')


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@main_bp.route('/analytics')
def analytics():
    """Analytics dashboard page."""
    game_state = get_game_state()
    if not game_state:
        flash('No active game to analyze.', 'warning')
        return redirect(url_for('main.menu'))

    return render_template('analytics.html', game_state=game_state)


@main_bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')