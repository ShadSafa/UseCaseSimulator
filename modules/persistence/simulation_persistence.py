from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import os
from .data_serializer import DataSerializer
from .company_persistence import CompanyPersistence
from .market_persistence import MarketPersistence
from ..core.simulation_engine import SimulationEngine
from ..core.simulation_state import SimulationState


class SimulationPersistence:
    """Handles saving and loading of complete simulation states."""

    def __init__(self, serializer: Optional[DataSerializer] = None):
        self.serializer = serializer or DataSerializer()
        self.company_persistence = CompanyPersistence(serializer)
        self.market_persistence = MarketPersistence(serializer)

    def save_simulation(self, simulation_engine: SimulationEngine, filename: str) -> str:
        """Save a complete simulation state.

        Args:
            simulation_engine: SimulationEngine instance
            filename: Output filename (without extension)

        Returns:
            Path to the saved file
        """
        # Get current simulation state
        current_state = simulation_engine.get_current_state()
        if not current_state:
            raise ValueError("No active simulation to save")

        # Build comprehensive save data
        save_data = {
            'simulation_config': {
                'max_rounds': simulation_engine.config.max_rounds,
                'num_competitors': simulation_engine.config.num_competitors,
                'initial_market_demand': simulation_engine.config.initial_market_demand,
                'market_volatility': simulation_engine.config.market_volatility,
                'event_frequency': simulation_engine.config.event_frequency
            },
            'current_state': current_state.to_dict(),
            'round_manager': {
                'current_round': simulation_engine.round_manager.get_current_round(),
                'max_rounds': simulation_engine.round_manager.max_rounds,
                'is_simulation_over': simulation_engine.round_manager.is_simulation_over()
            },
            'event_manager': {
                'active_events': simulation_engine.event_manager.get_active_events(),
                'event_history': simulation_engine.event_manager.get_event_history()
            },
            'simulation_history': simulation_engine.simulation_history,
            '_metadata': {
                'saved_at': datetime.now(),
                'version': '1.0',
                'type': 'simulation',
                'round_number': current_state.round_number,
                'company_name': current_state.player_company.name
            }
        }

        return self.serializer.serialize_to_json(save_data, filename)

    def load_simulation(self, filename: str) -> SimulationEngine:
        """Load a complete simulation state.

        Args:
            filename: Filename to load (without extension)

        Returns:
            SimulationEngine instance with loaded state

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data is invalid
        """
        save_data = self.serializer.deserialize_from_json(filename)

        # Validate data
        if not self.serializer.validate_save_data(save_data, 'simulation'):
            raise ValueError(f"Invalid simulation data in file: {filename}")

        # Extract configuration
        config_data = save_data.get('simulation_config', {})
        from ..core.simulation_engine import SimulationConfig
        config = SimulationConfig(**config_data)

        # Create simulation engine
        simulation_engine = SimulationEngine(config)

        # Restore round manager
        round_data = save_data.get('round_manager', {})
        simulation_engine.round_manager.current_round = round_data.get('current_round', 0)

        # Restore event manager
        event_data = save_data.get('event_manager', {})
        if 'active_events' in event_data:
            simulation_engine.event_manager.active_events = event_data['active_events']
        if 'event_history' in event_data:
            simulation_engine.event_manager.event_history = event_data['event_history']

        # Restore simulation state
        state_data = save_data.get('current_state')
        simulation_engine.current_state = SimulationState.from_dict(state_data)

        # Restore simulation history
        simulation_engine.simulation_history = save_data.get('simulation_history', [])

        return simulation_engine

    def save_simulation_snapshot(self, simulation_engine: SimulationEngine) -> str:
        """Save a snapshot of the current simulation state.

        Args:
            simulation_engine: SimulationEngine instance

        Returns:
            Path to the saved snapshot
        """
        current_state = simulation_engine.get_current_state()
        if not current_state:
            raise ValueError("No active simulation to snapshot")

        filename = f"simulation_snapshot_round_{current_state.round_number}"
        return self.save_simulation(simulation_engine, filename)

    def quick_save(self, simulation_engine: SimulationEngine) -> str:
        """Perform a quick save with automatic naming.

        Args:
            simulation_engine: SimulationEngine instance

        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quicksave_{timestamp}"
        return self.save_simulation(simulation_engine, filename)

    def auto_save(self, simulation_engine: SimulationEngine, interval: int = 5) -> Optional[str]:
        """Perform an auto-save if the current round is a multiple of the interval.

        Args:
            simulation_engine: SimulationEngine instance
            interval: Round interval for auto-saves

        Returns:
            Path to the saved file if auto-save was performed, None otherwise
        """
        current_round = simulation_engine.round_manager.get_current_round()
        if current_round > 0 and current_round % interval == 0:
            filename = f"autosave_round_{current_round}"
            return self.save_simulation(simulation_engine, filename)
        return None

    def list_simulation_saves(self) -> List[Dict[str, Any]]:
        """List all saved simulation files with metadata.

        Returns:
            List of dictionaries containing file information
        """
        json_files = self.serializer.list_save_files('json')
        simulation_files = []

        for filename in json_files:
            if filename.startswith(('simulation_', 'quicksave_', 'autosave_')):
                file_info = self.serializer.get_file_info(filename, 'json')
                if file_info:
                    # Try to get basic info from the file
                    try:
                        data = self.serializer.deserialize_from_json(filename)
                        if self.serializer.validate_save_data(data, 'simulation'):
                            metadata = data.get('_metadata', {})
                            file_info['round_number'] = metadata.get('round_number', 0)
                            file_info['company_name'] = metadata.get('company_name', 'Unknown')
                            file_info['saved_at'] = metadata.get('saved_at')
                            file_info['save_type'] = self._get_save_type(filename)
                    except:
                        pass  # Skip files that can't be read

                    simulation_files.append(file_info)

        return simulation_files

    def _get_save_type(self, filename: str) -> str:
        """Determine the type of save file."""
        if filename.startswith('quicksave_'):
            return 'quick_save'
        elif filename.startswith('autosave_'):
            return 'auto_save'
        elif filename.startswith('simulation_snapshot_'):
            return 'snapshot'
        else:
            return 'manual_save'

    def delete_simulation_save(self, filename: str) -> bool:
        """Delete a simulation save file.

        Args:
            filename: Filename to delete (without extension)

        Returns:
            True if deleted successfully
        """
        return self.serializer.delete_save_file(filename, 'json')

    def export_simulation_to_csv(self, simulation_engine: SimulationEngine, filename: str) -> str:
        """Export simulation data to CSV format.

        Args:
            simulation_engine: SimulationEngine instance
            filename: Output filename (without extension)

        Returns:
            Path to the exported CSV file
        """
        import csv

        filepath = Path(self.serializer.base_path) / f"{filename}.csv"

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Round', 'Revenue', 'Costs', 'Profit', 'Market Share', 'Customer Satisfaction', 'Efficiency'])

            # Write historical data
            for history_item in simulation_engine.simulation_history:
                company = history_item.get('player_company', {})
                financial = company.get('financial_data', {})
                market = company.get('market_data', {})
                operations = company.get('operations_data', {})

                writer.writerow([
                    history_item.get('round_number', 0),
                    financial.get('revenue', 0),
                    financial.get('costs', 0),
                    financial.get('profit', 0),
                    market.get('market_share', 0),
                    operations.get('customer_satisfaction', 0),
                    operations.get('efficiency', 0)
                ])

        return str(filepath)

    def get_simulation_backup(self, filename: str) -> Optional[str]:
        """Create a backup of a simulation save.

        Args:
            filename: Simulation save filename

        Returns:
            Path to backup file, or None if save doesn't exist
        """
        try:
            return self.serializer.create_backup(filename, 'json')
        except FileNotFoundError:
            return None

    def save_game_components_separately(self, simulation_engine: SimulationEngine,
                                       base_filename: str) -> Dict[str, str]:
        """Save different components of the simulation separately.

        Args:
            simulation_engine: SimulationEngine instance
            base_filename: Base filename for the saves

        Returns:
            Dictionary mapping component names to file paths
        """
        current_state = simulation_engine.get_current_state()
        if not current_state:
            raise ValueError("No active simulation to save")

        saved_files = {}

        # Save company
        company_file = self.company_persistence.save_company(
            current_state.player_company,
            f"{base_filename}_company"
        )
        saved_files['company'] = company_file

        # Save market
        market_file = self.market_persistence.save_market(
            current_state.market,
            f"{base_filename}_market"
        )
        saved_files['market'] = market_file

        # Save competitors
        competitors_data = {
            'competitors': current_state.competitors,
            '_metadata': {
                'saved_at': datetime.now(),
                'version': '1.0',
                'type': 'competitors',
                'round_number': current_state.round_number
            }
        }
        competitors_file = self.serializer.serialize_to_json(competitors_data, f"{base_filename}_competitors")
        saved_files['competitors'] = competitors_file

        return saved_files

    def load_game_components_separately(self, base_filename: str) -> Dict[str, Any]:
        """Load different components of the simulation separately.

        Args:
            base_filename: Base filename for the saves

        Returns:
            Dictionary containing loaded components
        """
        components = {}

        try:
            # Load company
            components['company'] = self.company_persistence.load_company(f"{base_filename}_company")
        except FileNotFoundError:
            pass

        try:
            # Load market
            components['market'] = self.market_persistence.load_market(f"{base_filename}_market")
        except FileNotFoundError:
            pass

        try:
            # Load competitors
            competitors_data = self.serializer.deserialize_from_json(f"{base_filename}_competitors")
            components['competitors'] = competitors_data.get('competitors', [])
        except FileNotFoundError:
            pass

        return components

    def get_save_file_summary(self, filename: str) -> Dict[str, Any]:
        """Get a summary of what's in a save file without loading the full data.

        Args:
            filename: Save filename (without extension)

        Returns:
            Dictionary with save file summary
        """
        try:
            data = self.serializer.deserialize_from_json(filename)
            metadata = data.get('_metadata', {})

            summary = {
                'filename': filename,
                'save_type': self._get_save_type(filename),
                'round_number': metadata.get('round_number', 0),
                'company_name': metadata.get('company_name', 'Unknown'),
                'saved_at': metadata.get('saved_at'),
                'version': metadata.get('version', 'Unknown'),
                'has_company_data': 'player_company' in data.get('current_state', {}),
                'has_market_data': 'market' in data.get('current_state', {}),
                'has_competitors': 'competitors' in data.get('current_state', {}),
                'simulation_complete': data.get('round_manager', {}).get('is_simulation_over', False)
            }

            return summary

        except Exception as e:
            return {
                'filename': filename,
                'error': str(e),
                'readable': False
            }

    def cleanup_old_saves(self, keep_recent: int = 10, save_type: str = 'auto_save') -> int:
        """Clean up old save files, keeping only the most recent ones.

        Args:
            keep_recent: Number of recent saves to keep
            save_type: Type of saves to clean up

        Returns:
            Number of files deleted
        """
        saves = self.list_simulation_saves()
        type_saves = [s for s in saves if s.get('save_type') == save_type]

        if len(type_saves) <= keep_recent:
            return 0

        # Sort by save time (newest first)
        type_saves.sort(key=lambda x: x.get('saved_at', datetime.min), reverse=True)

        # Delete old saves
        deleted_count = 0
        for save in type_saves[keep_recent:]:
            if self.delete_simulation_save(save['filename']):
                deleted_count += 1

        return deleted_count