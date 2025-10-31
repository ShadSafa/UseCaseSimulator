import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from ..core.market import Market
from ..core.company import Company
from ..persistence.data_serializer import DataSerializer


class ScenarioLoader:
    """Loads and manages market scenarios for the business simulation."""

    def __init__(self, scenarios_dir: str = "data/scenarios"):
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.serializer = DataSerializer(str(self.scenarios_dir))

    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Load a complete scenario by name.

        Args:
            scenario_name: Name of the scenario to load

        Returns:
            Dictionary containing scenario data

        Raises:
            FileNotFoundError: If scenario doesn't exist
            ValueError: If scenario data is invalid
        """
        scenario_file = self.scenarios_dir / f"{scenario_name}.json"

        if not scenario_file.exists():
            raise FileNotFoundError(f"Scenario '{scenario_name}' not found")

        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)

        # Validate scenario structure
        self._validate_scenario(scenario_data)

        return scenario_data

    def list_available_scenarios(self) -> List[Dict[str, Any]]:
        """List all available scenarios with metadata.

        Returns:
            List of scenario information dictionaries
        """
        scenarios = []

        for scenario_file in self.scenarios_dir.glob("*.json"):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)

                if self._is_valid_scenario(scenario_data):
                    scenario_info = {
                        'name': scenario_file.stem,
                        'title': scenario_data.get('title', scenario_file.stem),
                        'description': scenario_data.get('description', ''),
                        'difficulty': scenario_data.get('difficulty', 'normal'),
                        'estimated_duration': scenario_data.get('estimated_duration', 10),
                        'tags': scenario_data.get('tags', []),
                        'created_at': scenario_data.get('created_at'),
                        'version': scenario_data.get('version', '1.0')
                    }
                    scenarios.append(scenario_info)

            except (json.JSONDecodeError, KeyError):
                continue  # Skip invalid scenario files

        return scenarios

    def get_scenario_info(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific scenario.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Scenario information dictionary, or None if not found
        """
        try:
            scenario_data = self.load_scenario(scenario_name)
            return {
                'name': scenario_name,
                'title': scenario_data.get('title', scenario_name),
                'description': scenario_data.get('description', ''),
                'difficulty': scenario_data.get('difficulty', 'normal'),
                'estimated_duration': scenario_data.get('estimated_duration', 10),
                'tags': scenario_data.get('tags', []),
                'objectives': scenario_data.get('objectives', []),
                'challenges': scenario_data.get('challenges', []),
                'tips': scenario_data.get('tips', []),
                'market_conditions': scenario_data.get('market_conditions', {}),
                'starting_conditions': scenario_data.get('starting_conditions', {}),
                'created_at': scenario_data.get('created_at'),
                'version': scenario_data.get('version', '1.0')
            }
        except (FileNotFoundError, ValueError):
            return None

    def create_scenario_from_simulation(self, simulation_engine, scenario_name: str,
                                       title: str = "", description: str = "") -> str:
        """Create a new scenario based on current simulation state.

        Args:
            simulation_engine: Current simulation engine instance
            scenario_name: Name for the new scenario
            title: Display title for the scenario
            description: Description of the scenario

        Returns:
            Path to the created scenario file
        """
        current_state = simulation_engine.get_current_state()
        if not current_state:
            raise ValueError("No active simulation to create scenario from")

        scenario_data = {
            'title': title or scenario_name,
            'description': description,
            'difficulty': 'custom',
            'estimated_duration': simulation_engine.config.max_rounds,
            'tags': ['custom', 'generated'],
            'version': '1.0',
            'created_at': datetime.now().isoformat(),

            'market_conditions': {
                'demand_level': current_state.market.state.demand_level,
                'price_index': current_state.market.state.price_index,
                'competition_intensity': current_state.market.state.competition_intensity,
                'economic_indicators': current_state.market.state.economic_indicators,
                'trend_factors': current_state.market.state.trend_factors
            },

            'starting_conditions': {
                'company': current_state.player_company.to_dict(),
                'competitors': current_state.competitors,
                'round_number': current_state.round_number
            },

            'simulation_config': {
                'max_rounds': simulation_engine.config.max_rounds,
                'num_competitors': simulation_engine.config.num_competitors,
                'initial_market_demand': simulation_engine.config.initial_market_demand,
                'market_volatility': simulation_engine.config.market_volatility,
                'event_frequency': simulation_engine.config.event_frequency
            }
        }

        scenario_file = self.scenarios_dir / f"{scenario_name}.json"
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, default=str)

        return str(scenario_file)

    def apply_scenario_to_simulation(self, scenario_name: str, simulation_engine) -> bool:
        """Apply a scenario to an existing simulation engine.

        Args:
            scenario_name: Name of the scenario to apply
            simulation_engine: Simulation engine to modify

        Returns:
            True if scenario was applied successfully
        """
        try:
            scenario_data = self.load_scenario(scenario_name)

            # Update market conditions
            market_conditions = scenario_data.get('market_conditions', {})
            if market_conditions:
                simulation_engine.current_state.market.state.demand_level = market_conditions.get('demand_level', 1000.0)
                simulation_engine.current_state.market.state.price_index = market_conditions.get('price_index', 1.0)
                simulation_engine.current_state.market.state.competition_intensity = market_conditions.get('competition_intensity', 0.5)
                simulation_engine.current_state.market.state.economic_indicators = market_conditions.get('economic_indicators', {})
                simulation_engine.current_state.market.state.trend_factors = market_conditions.get('trend_factors', {})

            # Update starting conditions if applicable
            starting_conditions = scenario_data.get('starting_conditions', {})
            if starting_conditions:
                if 'company' in starting_conditions:
                    company_data = starting_conditions['company']
                    simulation_engine.current_state.player_company = Company.from_dict(company_data)

                if 'competitors' in starting_conditions:
                    simulation_engine.current_state.competitors = starting_conditions['competitors']

            # Update simulation config
            sim_config = scenario_data.get('simulation_config', {})
            if sim_config:
                from ..core.simulation_engine import SimulationConfig
                simulation_engine.config = SimulationConfig(**sim_config)

            return True

        except Exception as e:
            print(f"Error applying scenario: {e}")
            return False

    def delete_scenario(self, scenario_name: str) -> bool:
        """Delete a scenario file.

        Args:
            scenario_name: Name of the scenario to delete

        Returns:
            True if deleted successfully, False if not found
        """
        scenario_file = self.scenarios_dir / f"{scenario_name}.json"

        if scenario_file.exists():
            scenario_file.unlink()
            return True
        return False

    def validate_scenario_file(self, scenario_name: str) -> Dict[str, Any]:
        """Validate a scenario file and return validation results.

        Args:
            scenario_name: Name of the scenario to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'scenario_name': scenario_name,
            'is_valid': False,
            'errors': [],
            'warnings': []
        }

        try:
            scenario_data = self.load_scenario(scenario_name)

            # Check required fields
            required_fields = ['market_conditions', 'starting_conditions']
            for field in required_fields:
                if field not in scenario_data:
                    validation_result['errors'].append(f"Missing required field: {field}")

            # Validate market conditions
            market_conditions = scenario_data.get('market_conditions', {})
            if not isinstance(market_conditions, dict):
                validation_result['errors'].append("market_conditions must be a dictionary")
            else:
                required_market_fields = ['demand_level', 'price_index', 'competition_intensity']
                for field in required_market_fields:
                    if field not in market_conditions:
                        validation_result['warnings'].append(f"Missing market field: {field}")

            # Validate starting conditions
            starting_conditions = scenario_data.get('starting_conditions', {})
            if not isinstance(starting_conditions, dict):
                validation_result['errors'].append("starting_conditions must be a dictionary")

            # Check for valid JSON structure
            json.dumps(scenario_data, default=str)  # This will raise an exception if not serializable

            validation_result['is_valid'] = len(validation_result['errors']) == 0

        except FileNotFoundError:
            validation_result['errors'].append("Scenario file not found")
        except json.JSONDecodeError as e:
            validation_result['errors'].append(f"Invalid JSON: {e}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")

        return validation_result

    def _validate_scenario(self, scenario_data: Dict[str, Any]):
        """Validate scenario data structure.

        Args:
            scenario_data: Scenario data to validate

        Raises:
            ValueError: If scenario data is invalid
        """
        if not isinstance(scenario_data, dict):
            raise ValueError("Scenario data must be a dictionary")

        required_fields = ['market_conditions']
        for field in required_fields:
            if field not in scenario_data:
                raise ValueError(f"Scenario missing required field: {field}")

    def _is_valid_scenario(self, scenario_data: Dict[str, Any]) -> bool:
        """Check if scenario data represents a valid scenario."""
        try:
            self._validate_scenario(scenario_data)
            return True
        except ValueError:
            return False

    def get_scenario_templates(self) -> List[str]:
        """Get list of available scenario templates.

        Returns:
            List of template scenario names
        """
        templates = []
        for scenario_file in self.scenarios_dir.glob("template_*.json"):
            templates.append(scenario_file.stem.replace('template_', ''))

        return templates

    def create_scenario_from_template(self, template_name: str, scenario_name: str,
                                    customizations: Dict[str, Any] = None) -> str:
        """Create a new scenario from a template with customizations.

        Args:
            template_name: Name of the template to use
            scenario_name: Name for the new scenario
            customizations: Dictionary of custom values to override

        Returns:
            Path to the created scenario file
        """
        template_file = self.scenarios_dir / f"template_{template_name}.json"

        if not template_file.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found")

        with open(template_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)

        # Apply customizations
        if customizations:
            self._apply_customizations(scenario_data, customizations)

        # Update metadata
        scenario_data['title'] = scenario_name
        scenario_data['created_at'] = datetime.now().isoformat()
        scenario_data['tags'] = scenario_data.get('tags', []) + ['customized']

        # Save new scenario
        scenario_file = self.scenarios_dir / f"{scenario_name}.json"
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, default=str)

        return str(scenario_file)

    def _apply_customizations(self, scenario_data: Dict[str, Any], customizations: Dict[str, Any]):
        """Apply customizations to scenario data."""
        for key, value in customizations.items():
            if '.' in key:
                # Handle nested keys like "market_conditions.demand_level"
                keys = key.split('.')
                current = scenario_data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            else:
                scenario_data[key] = value