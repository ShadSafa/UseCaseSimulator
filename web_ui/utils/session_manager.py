"""
Session management utilities for the web UI.
Handles game state persistence in Flask sessions.
"""

from flask import session
from typing import Optional, Dict, Any
from modules.core.simulation_state import SimulationState


def get_game_state() -> Optional[SimulationState]:
    """Get the current game state from session."""
    game_state_data = session.get('game_state')
    if game_state_data:
        try:
            return SimulationState.from_dict(game_state_data)
        except Exception:
            # Invalid session data, clear it
            clear_game_state()
            return None
    return None


def set_game_state(game_state: SimulationState):
    """Store game state in session."""
    session['game_state'] = game_state.to_dict()
    session.modified = True


def update_game_state(updates: Dict[str, Any]):
    """Update specific parts of the game state."""
    current_state = get_game_state()
    if current_state:
        state_dict = current_state.to_dict()
        state_dict.update(updates)
        try:
            updated_state = SimulationState.from_dict(state_dict)
            set_game_state(updated_state)
        except Exception:
            pass  # Keep existing state if update fails


def clear_game_state():
    """Clear the game state from session."""
    if 'game_state' in session:
        del session['game_state']
    if 'game_setup' in session:
        del session['game_setup']
    if 'load_request' in session:
        del session['load_request']
    session.modified = True


def has_active_game() -> bool:
    """Check if there's an active game in session."""
    return get_game_state() is not None


def get_game_setup() -> Optional[Dict[str, Any]]:
    """Get game setup data from session."""
    return session.get('game_setup')


def set_game_setup(setup_data: Dict[str, Any]):
    """Store game setup data in session."""
    session['game_setup'] = setup_data
    session.modified = True


def get_load_request() -> Optional[str]:
    """Get load request from session."""
    return session.get('load_request')


def clear_load_request():
    """Clear load request from session."""
    if 'load_request' in session:
        del session['load_request']
    session.modified = True


def initialize_session():
    """Initialize session with default values."""
    if 'session_initialized' not in session:
        session['session_initialized'] = True
        session['start_time'] = __import__('datetime').datetime.utcnow().isoformat()
        session.modified = True


def get_session_info() -> Dict[str, Any]:
    """Get session information for debugging."""
    return {
        'has_game_state': 'game_state' in session,
        'has_game_setup': 'game_setup' in session,
        'has_load_request': 'load_request' in session,
        'session_initialized': session.get('session_initialized', False),
        'start_time': session.get('start_time')
    }