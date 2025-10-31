"""
Game-specific routes for the Use Case Simulator web application.
Handles game flow, decisions, and round management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..utils.session_manager import get_game_state, set_game_state, clear_game_state, has_active_game
import os
import sys

# Add parent directory to path for core imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.core.simulation_state import SimulationState

game_bp = Blueprint('game', __name__)


@game_bp.route('/initialize', methods=['POST'])
def initialize_game():
    """Initialize a new game session."""
    try:
        # Get setup data from session
        setup_data = session.get('game_setup')
        if not setup_data:
            flash('Game setup data not found. Please start over.', 'error')
            return redirect(url_for('main.new_game'))

        company_name = setup_data.get('company_name', 'My Company')
        difficulty = setup_data.get('difficulty', 'medium')
        scenario = setup_data.get('scenario', 'default')

        # Create simulation engine
        config = SimulationConfig()
        engine = SimulationEngine(config)

        # Initialize simulation
        game_state = engine.initialize_simulation(scenario)

        # Update company name
        game_state.player_company.name = company_name

        # Store in session
        set_game_state(game_state)
        session['engine'] = engine

        flash(f'Welcome to Use Case Simulator, {company_name}!', 'success')
        return redirect(url_for('main.dashboard'))

    except Exception as e:
        flash(f'Error initializing game: {str(e)}', 'error')
        return redirect(url_for('main.new_game'))


@game_bp.route('/decision')
def decision_phase():
    """Show decision input form."""
    if not has_active_game():
        flash('No active game. Please start a new simulation.', 'warning')
        return redirect(url_for('main.menu'))

    game_state = get_game_state()
    return render_template('decisions.html', game_state=game_state)


@game_bp.route('/process-decision', methods=['POST'])
def process_decision():
    """Process player decisions."""
    if not has_active_game():
        flash('No active game session.', 'error')
        return redirect(url_for('main.menu'))

    try:
        # Get form data
        decisions = {}

        # Pricing decision
        if request.form.get('pricing'):
            decisions['pricing'] = {'price': float(request.form.get('pricing'))}

        # Marketing budget
        if request.form.get('marketing'):
            decisions['marketing'] = {'budget': float(request.form.get('marketing'))}

        # Capacity expansion
        if request.form.get('capacity_expansion'):
            decisions['capacity_expansion'] = {'expansion_amount': float(request.form.get('capacity_expansion'))}

        # Quality improvement
        if request.form.get('quality_improvement'):
            decisions['quality_improvement'] = {'investment': float(request.form.get('quality_improvement'))}

        # Hiring
        if request.form.get('hiring'):
            decisions['hiring'] = {'num_employees': int(request.form.get('hiring'))}

        # Equipment purchase
        if request.form.get('equipment_purchase'):
            decisions['equipment_purchase'] = {'equipment_value': float(request.form.get('equipment_purchase'))}

        # Get engine from session
        engine = session.get('engine')
        if not engine:
            flash('Game session expired. Please start over.', 'error')
            clear_game_state()
            return redirect(url_for('main.menu'))

        # Run the round
        round_results = engine.run_round(decisions)

        # Update game state
        updated_state = SimulationState.from_dict(round_results['game_state'])
        set_game_state(updated_state)

        flash(f'Round {round_results["round_number"]} completed successfully!', 'success')
        return redirect(url_for('game.round_results'))

    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('game.decision_phase'))
    except Exception as e:
        flash(f'Error processing decision: {str(e)}', 'error')
        return redirect(url_for('game.decision_phase'))


@game_bp.route('/round-results')
def round_results():
    """Show round results."""
    if not has_active_game():
        flash('No active game. Please start a new simulation.', 'warning')
        return redirect(url_for('main.menu'))

    game_state = get_game_state()

    # Get round results from session or calculate
    round_results = session.get('last_round_results', {})

    return render_template('results.html',
                         game_state=game_state,
                         round_results=round_results)


@game_bp.route('/next-round')
def next_round():
    """Advance to next round."""
    if not has_active_game():
        flash('No active game. Please start a new simulation.', 'warning')
        return redirect(url_for('main.menu'))

    # Check if game is over
    game_state = get_game_state()
    engine = session.get('engine')

    if engine and engine.round_manager.is_simulation_over():
        return redirect(url_for('game.game_over'))

    # Go to decision phase
    return redirect(url_for('game.decision_phase'))


@game_bp.route('/game-over')
def game_over():
    """Show game over screen."""
    if not has_active_game():
        flash('No active game. Please start a new simulation.', 'warning')
        return redirect(url_for('main.menu'))

    game_state = get_game_state()
    return render_template('game_over.html', game_state=game_state)


@game_bp.route('/quit', methods=['POST'])
def quit_game():
    """Quit the current game."""
    clear_game_state()
    flash('Game ended. Thanks for playing!', 'info')
    return redirect(url_for('main.menu'))


@game_bp.route('/save', methods=['POST'])
def save_game():
    """Save the current game."""
    if not has_active_game():
        flash('No active game to save.', 'warning')
        return redirect(url_for('main.dashboard'))

    try:
        save_name = request.form.get('save_name', f'save_{__import__("time").time()}')

        engine = session.get('engine')
        if engine:
            success = engine.save_simulation(save_name)
            if success:
                flash(f'Game saved as "{save_name}"', 'success')
            else:
                flash('Failed to save game.', 'error')
        else:
            flash('Game session expired.', 'error')

    except Exception as e:
        flash(f'Error saving game: {str(e)}', 'error')

    return redirect(url_for('main.dashboard'))


@game_bp.route('/load/<save_name>')
def load_specific_game(save_name):
    """Load a specific saved game."""
    try:
        config = SimulationConfig()
        engine = SimulationEngine(config)

        game_state = engine.load_simulation(save_name)

        if game_state:
            set_game_state(game_state)
            session['engine'] = engine
            flash(f'Game "{save_name}" loaded successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(f'Failed to load game "{save_name}".', 'error')
            return redirect(url_for('main.load_game'))

    except Exception as e:
        flash(f'Error loading game: {str(e)}', 'error')
        return redirect(url_for('main.load_game'))