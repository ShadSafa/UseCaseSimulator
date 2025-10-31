from typing import Dict, Any, Optional, List
from datetime import datetime
from .scenario_loader import ScenarioLoader
from ..core.simulation_engine import SimulationEngine
from ..core.market import Market
from ..core.company import Company


class ScenarioManager:
    """Manages scenario loading and switching for the simulation."""

    def __init__(self, scenarios_dir: str = "data/scenarios"):
        self.loader = ScenarioLoader(scenarios_dir)
        self.current_scenario: Optional[str] = None
        self.scenario_history: List[Dict[str, Any]] = []

    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Load a scenario by name.

        Args:
            scenario_name: Name of the scenario to load

        Returns:
            Scenario data dictionary

        Raises:
            FileNotFoundError: If scenario doesn't exist
            ValueError: If scenario data is invalid
        """
        scenario_data = self.loader.load_scenario(scenario_name)
        self.current_scenario = scenario_name

        # Record in history
        self.scenario_history.append({
            'scenario_name': scenario_name,
            'loaded_at': datetime.now(),
            'action': 'loaded'
        })

        return scenario_data

    def apply_scenario_to_simulation(self, scenario_name: str,
                                   simulation_engine: SimulationEngine) -> bool:
        """Apply a scenario to a running simulation.

        Args:
            scenario_name: Name of the scenario to apply
            simulation_engine: The simulation engine to modify

        Returns:
            True if scenario was applied successfully
        """
        try:
            success = self.loader.apply_scenario_to_simulation(scenario_name, simulation_engine)

            if success:
                self.current_scenario = scenario_name
                self.scenario_history.append({
                    'scenario_name': scenario_name,
                    'applied_at': datetime.now(),
                    'action': 'applied_to_simulation'
                })

            return success

        except Exception as e:
            print(f"Error applying scenario: {e}")
            return False

    def create_new_simulation_from_scenario(self, scenario_name: str) -> SimulationEngine:
        """Create a new simulation engine initialized with a scenario.

        Args:
            scenario_name: Name of the scenario to use

        Returns:
            New SimulationEngine instance configured for the scenario

        Raises:
            FileNotFoundError: If scenario doesn't exist
            ValueError: If scenario data is invalid
        """
        scenario_data = self.load_scenario(scenario_name)

        # Extract simulation config
        sim_config_data = scenario_data.get('simulation_config', {})
        from ..core.simulation_engine import SimulationConfig
        config = SimulationConfig(**sim_config_data)

        # Create simulation engine
        simulation_engine = SimulationEngine(config)

        # Initialize with scenario data
        self._initialize_simulation_from_scenario(simulation_engine, scenario_data)

        return simulation_engine

    def switch_scenario_during_simulation(self, new_scenario_name: str,
                                        simulation_engine: SimulationEngine,
                                        preserve_company: bool = True) -> bool:
        """Switch to a different scenario during an active simulation.

        Args:
            new_scenario_name: Name of the new scenario
            simulation_engine: Current simulation engine
            preserve_company: Whether to preserve the player's company state

        Returns:
            True if scenario switch was successful
        """
        try:
            # Load new scenario
            new_scenario_data = self.load_scenario(new_scenario_name)

            # Store current company state if preserving
            company_backup = None
            if preserve_company and simulation_engine.current_state:
                company_backup = simulation_engine.current_state.player_company

            # Apply new scenario market conditions
            market_conditions = new_scenario_data.get('market_conditions', {})
            if market_conditions and simulation_engine.current_state:
                simulation_engine.current_state.market.state.demand_level = market_conditions.get('demand_level', 1000.0)
                simulation_engine.current_state.market.state.price_index = market_conditions.get('price_index', 1.0)
                simulation_engine.current_state.market.state.competition_intensity = market_conditions.get('competition_intensity', 0.5)
                simulation_engine.current_state.market.state.economic_indicators = market_conditions.get('economic_indicators', {})
                simulation_engine.current_state.market.state.trend_factors = market_conditions.get('trend_factors', {})

            # Update competitors if specified in scenario
            starting_conditions = new_scenario_data.get('starting_conditions', {})
            if 'competitors' in starting_conditions and simulation_engine.current_state:
                simulation_engine.current_state.competitors = starting_conditions['competitors']

            # Restore company if preserving
            if preserve_company and company_backup and simulation_engine.current_state:
                simulation_engine.current_state.player_company = company_backup

            # Update simulation config
            sim_config = new_scenario_data.get('simulation_config', {})
            if sim_config:
                from ..core.simulation_engine import SimulationConfig
                simulation_engine.config = SimulationConfig(**sim_config)

            self.current_scenario = new_scenario_name
            self.scenario_history.append({
                'scenario_name': new_scenario_name,
                'switched_at': datetime.now(),
                'action': 'switched_during_simulation',
                'preserved_company': preserve_company
            })

            return True

        except Exception as e:
            print(f"Error switching scenario: {e}")
            return False

    def create_scenario_from_template(self, template_name: str, scenario_name: str,
                                    customizations: Dict[str, Any] = None) -> str:
        """Create a new scenario from a template.

        Args:
            template_name: Name of the template to use
            scenario_name: Name for the new scenario
            customizations: Optional custom values to override

        Returns:
            Path to the created scenario file
        """
        return self.loader.create_scenario_from_template(template_name, scenario_name, customizations)

    def create_scenario_from_current_state(self, simulation_engine: SimulationEngine,
                                         scenario_name: str, title: str = "",
                                         description: str = "") -> str:
        """Create a scenario from the current simulation state.

        Args:
            simulation_engine: Current simulation engine
            scenario_name: Name for the new scenario
            title: Display title
            description: Description

        Returns:
            Path to the created scenario file
        """
        return self.loader.create_scenario_from_simulation(
            simulation_engine, scenario_name, title, description
        )

    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of all available scenarios.

        Returns:
            List of scenario information dictionaries
        """
        return self.loader.list_available_scenarios()

    def get_scenario_info(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a scenario.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Scenario information dictionary, or None if not found
        """
        return self.loader.get_scenario_info(scenario_name)

    def validate_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Validate a scenario file.

        Args:
            scenario_name: Name of the scenario to validate

        Returns:
            Validation results dictionary
        """
        return self.loader.validate_scenario_file(scenario_name)

    def get_scenario_history(self) -> List[Dict[str, Any]]:
        """Get the history of scenario loading and switching.

        Returns:
            List of scenario history entries
        """
        return self.scenario_history.copy()

    def get_current_scenario(self) -> Optional[str]:
        """Get the name of the currently active scenario.

        Returns:
            Current scenario name, or None if no scenario is active
        """
        return self.current_scenario

    def reset_scenario(self):
        """Reset the current scenario state."""
        self.current_scenario = None

    def get_scenarios_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get scenarios filtered by difficulty level.

        Args:
            difficulty: Difficulty level ("easy", "medium", "hard")

        Returns:
            List of scenarios matching the difficulty
        """
        all_scenarios = self.get_available_scenarios()
        return [s for s in all_scenarios if s.get('difficulty') == difficulty]

    def get_scenarios_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get scenarios filtered by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of scenarios with the specified tag
        """
        all_scenarios = self.get_available_scenarios()
        return [s for s in all_scenarios if tag in s.get('tags', [])]

    def recommend_scenario(self, player_experience: str = "beginner") -> Optional[str]:
        """Recommend a scenario based on player experience level.

        Args:
            player_experience: Experience level ("beginner", "intermediate", "advanced")

        Returns:
            Recommended scenario name, or None if no recommendation
        """
        experience_map = {
            "beginner": "easy",
            "intermediate": "medium",
            "advanced": "hard"
        }

        difficulty = experience_map.get(player_experience, "medium")
        scenarios = self.get_scenarios_by_difficulty(difficulty)

        if scenarios:
            # Return the first scenario (could be made more sophisticated)
            return scenarios[0]['name']

        return None

    def _initialize_simulation_from_scenario(self, simulation_engine: SimulationEngine,
                                           scenario_data: Dict[str, Any]):
        """Initialize a simulation engine with scenario data.

        Args:
            simulation_engine: SimulationEngine to initialize
            scenario_data: Scenario data to apply
        """
        # Initialize simulation
        simulation_engine.initialize_simulation()

        # Apply market conditions
        market_conditions = scenario_data.get('market_conditions', {})
        if market_conditions:
            simulation_engine.current_state.market.state.demand_level = market_conditions.get('demand_level', 1000.0)
            simulation_engine.current_state.market.state.price_index = market_conditions.get('price_index', 1.0)
            simulation_engine.current_state.market.state.competition_intensity = market_conditions.get('competition_intensity', 0.5)
            simulation_engine.current_state.market.state.economic_indicators = market_conditions.get('economic_indicators', {})
            simulation_engine.current_state.market.state.trend_factors = market_conditions.get('trend_factors', {})

        # Apply starting conditions
        starting_conditions = scenario_data.get('starting_conditions', {})

        if 'company' in starting_conditions:
            company_data = starting_conditions['company']
            simulation_engine.current_state.player_company = Company.from_dict(company_data)

        if 'competitors' in starting_conditions:
            simulation_engine.current_state.competitors = starting_conditions['competitors']

        if 'round_number' in starting_conditions:
            simulation_engine.current_state.round_number = starting_conditions['round_number']
            simulation_engine.round_manager.current_round = starting_conditions['round_number']

    def export_scenario(self, scenario_name: str, export_path: str) -> bool:
        """Export a scenario to a different location.

        Args:
            scenario_name: Name of the scenario to export
            export_path: Path to export to

        Returns:
            True if export was successful
        """
        try:
            scenario_data = self.load_scenario(scenario_name)
            import json
            with open(export_path, 'w') as f:
                json.dump(scenario_data, f, indent=2, default=str)
            return True
        except Exception:
            return False

    def import_scenario(self, import_path: str, scenario_name: str) -> bool:
        """Import a scenario from a file.

        Args:
            import_path: Path to the scenario file to import
            scenario_name: Name to give the imported scenario

        Returns:
            True if import was successful
        """
        try:
            import json
            with open(import_path, 'r') as f:
                scenario_data = json.load(f)

            # Validate the imported data
            self.loader._validate_scenario(scenario_data)

            # Save as new scenario
            scenario_file = self.loader.scenarios_dir / f"{scenario_name}.json"
            with open(scenario_file, 'w') as f:
                json.dump(scenario_data, f, indent=2, default=str)

            return True
        except Exception:
            return False