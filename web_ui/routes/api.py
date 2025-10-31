"""
API routes for the Use Case Simulator web application.
Provides REST endpoints for game operations and data retrieval.
"""

from flask import Blueprint, jsonify, request, session
from ..utils.session_manager import get_game_state, set_game_state, clear_game_state
import os
import sys

# Add parent directory to path for core imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.analytics.analytics_manager import AnalyticsManager

api_bp = Blueprint('api', __name__)

# Initialize analytics manager
analytics_manager = AnalyticsManager()


@api_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'usecasesimulator-api',
        'version': '1.0.0'
    })


@api_bp.route('/game/state')
def get_game_state():
    """Get current game state."""
    try:
        game_state = get_game_state()
        if game_state:
            return jsonify({
                'success': True,
                'data': game_state.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No active game session'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving game state: {str(e)}'
        }), 500


@api_bp.route('/game/new', methods=['POST'])
def create_new_game():
    """Create a new game session."""
    try:
        data = request.get_json() or {}
        company_name = data.get('company_name', 'My Company')
        difficulty = data.get('difficulty', 'medium')
        scenario = data.get('scenario', 'default')

        # Create simulation engine
        config = SimulationConfig()
        engine = SimulationEngine(config)

        # Initialize simulation
        game_state = engine.initialize_simulation(scenario)

        # Update company name
        game_state.player_company.name = company_name

        # Store in session
        set_game_state(game_state)

        # Store engine in session for later use
        session['engine'] = engine

        return jsonify({
            'success': True,
            'message': f'New game created for {company_name}',
            'data': game_state.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating new game: {str(e)}'
        }), 500


@api_bp.route('/game/load', methods=['POST'])
def load_game():
    """Load a saved game."""
    try:
        data = request.get_json() or {}
        save_name = data.get('save_name')

        if not save_name:
            return jsonify({
                'success': False,
                'message': 'Save name is required'
            }), 400

        # Create simulation engine
        config = SimulationConfig()
        engine = SimulationEngine(config)

        # Load simulation
        game_state = engine.load_simulation(save_name)

        if game_state:
            # Store in session
            set_game_state(game_state)
            session['engine'] = engine

            return jsonify({
                'success': True,
                'message': f'Game loaded: {save_name}',
                'data': game_state.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to load save: {save_name}'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading game: {str(e)}'
        }), 500


@api_bp.route('/game/save', methods=['POST'])
def save_game():
    """Save current game."""
    try:
        data = request.get_json() or {}
        save_name = data.get('save_name', f'save_{__import__("time").time()}')

        game_state = get_game_state()
        engine = session.get('engine')

        if not game_state or not engine:
            return jsonify({
                'success': False,
                'message': 'No active game to save'
            }), 400

        # Save simulation
        success = engine.save_simulation(save_name)

        if success:
            return jsonify({
                'success': True,
                'message': f'Game saved as: {save_name}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save game'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving game: {str(e)}'
        }), 500


@api_bp.route('/game/decision', methods=['POST'])
def submit_decision():
    """Submit player decisions for the current round."""
    try:
        data = request.get_json() or {}
        decisions = data.get('decisions', {})

        game_state = get_game_state()
        engine = session.get('engine')

        if not game_state or not engine:
            return jsonify({
                'success': False,
                'message': 'No active game session'
            }), 400

        # Process decisions
        processed_decisions = {}
        for key, value in decisions.items():
            if isinstance(value, dict):
                processed_decisions[key] = value
            else:
                processed_decisions[key] = {'value': value}

        # Run the round
        round_results = engine.run_round(processed_decisions)

        # Update game state
        updated_state = SimulationState.from_dict(round_results['game_state'])
        set_game_state(updated_state)

        return jsonify({
            'success': True,
            'message': f'Round {round_results["round_number"]} completed',
            'data': round_results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing decision: {str(e)}'
        }), 500


@api_bp.route('/analytics/kpis')
def get_kpi_data():
    """Get current KPI data."""
    try:
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                'success': False,
                'message': 'No active game session'
            }), 400

        # Get KPI data from game state
        kpis = game_state.player_company.get_kpis()

        return jsonify({
            'success': True,
            'data': {
                'kpis': kpis,
                'round': game_state.round_number,
                'company': game_state.player_company.name
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving KPI data: {str(e)}'
        }), 500


@api_bp.route('/analytics/charts')
def get_chart_data():
    """Get data for charts."""
    try:
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                'success': False,
                'message': 'No active game session'
            }), 400

        # Generate chart data
        chart_data = {
            'revenue_trend': [],
            'profit_trend': [],
            'market_share_trend': [],
            'rounds': []
        }

        # Get historical data (simplified - would need actual history)
        for i in range(1, game_state.round_number + 1):
            chart_data['rounds'].append(i)
            # Placeholder data - in real implementation, get from history
            chart_data['revenue_trend'].append(game_state.player_company.financial_data.revenue)
            chart_data['profit_trend'].append(game_state.player_company.financial_data.profit)
            chart_data['market_share_trend'].append(game_state.player_company.market_data.market_share)

        return jsonify({
            'success': True,
            'data': chart_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving chart data: {str(e)}'
        }), 500


@api_bp.route('/market/competitors')
def get_competitor_data():
    """Get competitor information."""
    try:
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                'success': False,
                'message': 'No active game session'
            }), 400

        competitors = game_state.competitors or []

        return jsonify({
            'success': True,
            'data': {
                'competitors': competitors,
                'count': len(competitors)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving competitor data: {str(e)}'
        }), 500


@api_bp.route('/game/scenarios')
def get_game_scenarios():
    """Get available game scenarios."""
    try:
        scenarios = [
            {
                'id': 'default',
                'name': 'Stable Market',
                'description': 'Predictable market conditions for learning basic business management',
                'difficulty': 'Easy'
            },
            {
                'id': 'booming_economy',
                'name': 'Booming Economy',
                'description': 'High growth environment - focus on scaling operations',
                'difficulty': 'Medium'
            },
            {
                'id': 'competitive_market',
                'name': 'Competitive Market',
                'description': 'Intense rivalry requiring strategic positioning',
                'difficulty': 'Hard'
            },
            {
                'id': 'recession',
                'name': 'Economic Recession',
                'description': 'Cost control and survival focus during downturn',
                'difficulty': 'Hard'
            }
        ]

        return jsonify({
            'success': True,
            'data': scenarios
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving scenarios: {str(e)}'
        }), 500


@api_bp.route('/scenarios/save', methods=['POST'])
def save_scenario():
    """Save a custom scenario."""
    try:
        data = request.get_json() or {}

        if not data:
            return jsonify({
                'success': False,
                'message': 'No scenario data provided'
            }), 400

        scenario_name = data.get('name', 'Unnamed Scenario')
        if not scenario_name or scenario_name == 'Unnamed Scenario':
            return jsonify({
                'success': False,
                'message': 'Scenario name is required'
            }), 400

        # Create scenarios directory if it doesn't exist
        scenarios_dir = os.path.join(os.getcwd(), 'data', 'scenarios')
        os.makedirs(scenarios_dir, exist_ok=True)

        # Save scenario as JSON file
        filename = f"{scenario_name.lower().replace(' ', '_').replace('/', '_')}.json"
        filepath = os.path.join(scenarios_dir, filename)

        # Remove metadata before saving
        save_data = data.copy()
        save_data.pop('created_at', None)  # Remove timestamp for cleaner JSON

        with open(filepath, 'w') as f:
            import json
            json.dump(save_data, f, indent=2)

        return jsonify({
            'success': True,
            'message': f'Scenario "{scenario_name}" saved successfully',
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving scenario: {str(e)}'
        }), 500


@api_bp.route('/scenarios')
def get_scenarios():
    """Get list of available custom scenarios."""
    try:
        scenarios_dir = os.path.join(os.getcwd(), 'data', 'scenarios')
        scenarios = []

        if os.path.exists(scenarios_dir):
            for file in os.listdir(scenarios_dir):
                if file.endswith('.json'):
                    try:
                        filepath = os.path.join(scenarios_dir, file)
                        with open(filepath, 'r') as f:
                            scenario_data = json.load(f)

                        scenarios.append({
                            'id': file.replace('.json', ''),
                            'name': scenario_data.get('name', 'Unnamed'),
                            'description': scenario_data.get('description', ''),
                            'difficulty': scenario_data.get('difficulty', 'medium'),
                            'max_rounds': scenario_data.get('max_rounds', 10),
                            'filename': file,
                            'created': os.path.getmtime(filepath)
                        })
                    except Exception as e:
                        # Skip corrupted scenario files
                        continue

        # Sort by creation time (newest first)
        scenarios.sort(key=lambda x: x['created'], reverse=True)

        return jsonify({
            'success': True,
            'data': scenarios
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving scenarios: {str(e)}'
        }), 500


@api_bp.route('/game/saves')
def get_save_files():
    """Get list of available save files."""
    try:
        saves_dir = os.path.join(os.getcwd(), 'data', 'saves')
        saves = []

        if os.path.exists(saves_dir):
            for file in os.listdir(saves_dir):
                if file.endswith('.json'):
                    save_name = file.replace('.json', '')
                    file_path = os.path.join(saves_dir, file)
                    mod_time = os.path.getmtime(file_path)

                    saves.append({
                        'name': save_name,
                        'filename': file,
                        'modified': mod_time
                    })

        # Sort by modification time (newest first)
        saves.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'data': saves
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving save files: {str(e)}'
        }), 500