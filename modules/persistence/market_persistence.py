from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import os
from .data_serializer import DataSerializer
from ..core.market import Market


class MarketPersistence:
    """Handles saving and loading of market data."""

    def __init__(self, serializer: Optional[DataSerializer] = None):
        self.serializer = serializer or DataSerializer()

    def save_market(self, market: Market, filename: Optional[str] = None) -> str:
        """Save a market object to file.

        Args:
            market: Market object to save
            filename: Optional custom filename (defaults to market_round_X)

        Returns:
            Path to the saved file
        """
        if filename is None:
            filename = f"market_round_{market.round_number}"

        # Convert market to dictionary
        market_data = market.to_dict()

        # Add metadata
        market_data['_metadata'] = {
            'saved_at': datetime.now(),
            'version': '1.0',
            'type': 'market',
            'round_number': market.round_number
        }

        return self.serializer.serialize_to_json(market_data, filename)

    def load_market(self, filename: str) -> Market:
        """Load a market object from file.

        Args:
            filename: Filename to load (without extension)

        Returns:
            Market object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data is invalid
        """
        market_data = self.serializer.deserialize_from_json(filename)

        # Validate data
        if not self.serializer.validate_save_data(market_data, 'market'):
            raise ValueError(f"Invalid market data in file: {filename}")

        # Remove metadata before creating market
        market_data.pop('_metadata', None)

        return Market.from_dict(market_data)

    def save_market_snapshot(self, market: Market) -> str:
        """Save a snapshot of current market state.

        Args:
            market: Market object

        Returns:
            Path to the saved snapshot
        """
        filename = f"market_snapshot_round_{market.round_number}"
        return self.save_market(market, filename)

    def list_market_saves(self) -> List[Dict[str, Any]]:
        """List all saved market files with metadata.

        Returns:
            List of dictionaries containing file information
        """
        json_files = self.serializer.list_save_files('json')
        market_files = []

        for filename in json_files:
            if filename.startswith('market_'):
                file_info = self.serializer.get_file_info(filename, 'json')
                if file_info:
                    # Try to get basic info from the file
                    try:
                        data = self.serializer.deserialize_from_json(filename)
                        if self.serializer.validate_save_data(data, 'market'):
                            file_info['round_number'] = data.get('round_number', 0)
                            file_info['has_metadata'] = '_metadata' in data
                            if file_info['has_metadata']:
                                file_info['saved_at'] = data['_metadata'].get('saved_at')
                    except:
                        pass  # Skip files that can't be read

                    market_files.append(file_info)

        return market_files

    def find_market_snapshots(self, start_round: int = 0, end_round: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find market snapshots within a round range.

        Args:
            start_round: Starting round number (inclusive)
            end_round: Ending round number (inclusive), None for all

        Returns:
            List of snapshot file information
        """
        all_saves = self.list_market_saves()
        snapshots = []

        for save_info in all_saves:
            filename = save_info['filename']
            if 'round_' in filename:
                try:
                    # Extract round number from filename
                    round_part = filename.split('round_')[-1]
                    round_num = int(round_part)
                    if round_num >= start_round and (end_round is None or round_num <= end_round):
                        save_info['round_number'] = round_num
                        snapshots.append(save_info)
                except (ValueError, IndexError):
                    continue

        # Sort by round number
        snapshots.sort(key=lambda x: x.get('round_number', 0))

        return snapshots

    def delete_market_save(self, filename: str) -> bool:
        """Delete a market save file.

        Args:
            filename: Filename to delete (without extension)

        Returns:
            True if deleted successfully
        """
        return self.serializer.delete_save_file(filename, 'json')

    def export_market_to_csv(self, market: Market, filename: str) -> str:
        """Export market data to CSV format.

        Args:
            market: Market object to export
            filename: Output filename (without extension)

        Returns:
            Path to the exported CSV file
        """
        import csv

        filepath = Path(self.serializer.base_path) / f"{filename}.csv"

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Category', 'Metric', 'Value'])

            # Write market state
            state = market.get_market_state()
            writer.writerow(['Market State', 'Demand Level', state.demand_level])
            writer.writerow(['Market State', 'Price Index', state.price_index])
            writer.writerow(['Market State', 'Competition Intensity', state.competition_intensity])

            # Write economic indicators
            for indicator, value in state.economic_indicators.items():
                writer.writerow(['Economic', indicator.replace('_', ' ').title(), value])

            # Write trend factors
            for factor, value in state.trend_factors.items():
                writer.writerow(['Trends', factor.title(), value])

            # Write competitor summary
            competitors = market.get_competitor_prices()
            writer.writerow(['Competitors', 'Count', len(competitors)])
            for i, price in enumerate(competitors):
                writer.writerow(['Competitors', f'Competitor {i+1} Price', price])

        return str(filepath)

    def get_market_backup(self, round_number: int) -> Optional[str]:
        """Create a backup of a market save for a specific round.

        Args:
            round_number: Round number

        Returns:
            Path to backup file, or None if no save exists
        """
        filename = f"market_round_{round_number}"
        try:
            return self.serializer.create_backup(filename, 'json')
        except FileNotFoundError:
            return None

    def save_market_scenario(self, market: Market, scenario_name: str) -> str:
        """Save a market as a reusable scenario.

        Args:
            market: Market object to save as scenario
            scenario_name: Name for the scenario

        Returns:
            Path to the saved scenario
        """
        filename = f"scenario_{scenario_name}"
        return self.save_market(market, filename)

    def load_market_scenario(self, scenario_name: str) -> Market:
        """Load a market scenario.

        Args:
            scenario_name: Name of the scenario to load

        Returns:
            Market object configured for the scenario
        """
        filename = f"scenario_{scenario_name}"
        return self.load_market(filename)

    def list_market_scenarios(self) -> List[str]:
        """List all saved market scenarios.

        Returns:
            List of scenario names
        """
        json_files = self.serializer.list_save_files('json')
        scenarios = []

        for filename in json_files:
            if filename.startswith('scenario_'):
                scenario_name = filename.replace('scenario_', '')
                scenarios.append(scenario_name)

        return scenarios

    def get_market_history(self, max_rounds: int = 10) -> List[Dict[str, Any]]:
        """Get historical market data for recent rounds.

        Args:
            max_rounds: Maximum number of recent rounds to include

        Returns:
            List of market data dictionaries
        """
        snapshots = self.find_market_snapshots()
        recent_snapshots = snapshots[-max_rounds:] if len(snapshots) > max_rounds else snapshots

        history = []
        for snapshot in recent_snapshots:
            try:
                market_data = self.serializer.deserialize_from_json(snapshot['filename'])
                market_data.pop('_metadata', None)  # Remove metadata
                history.append(market_data)
            except:
                continue  # Skip corrupted files

        return history

    def compare_market_states(self, round1: int, round2: int) -> Dict[str, Any]:
        """Compare two market states from different rounds.

        Args:
            round1: First round number
            round2: Second round number

        Returns:
            Dictionary containing comparison data
        """
        try:
            market1_data = self.serializer.deserialize_from_json(f"market_round_{round1}")
            market2_data = self.serializer.deserialize_from_json(f"market_round_{round2}")
        except FileNotFoundError:
            return {'error': 'One or both market saves not found'}

        comparison = {
            'round1': round1,
            'round2': round2,
            'demand_change': market2_data['state']['demand_level'] - market1_data['state']['demand_level'],
            'price_index_change': market2_data['state']['price_index'] - market1_data['state']['price_index'],
            'competition_change': market2_data['state']['competition_intensity'] - market1_data['state']['competition_intensity']
        }

        # Compare economic indicators
        econ_changes = {}
        for indicator in market1_data['state']['economic_indicators']:
            if indicator in market2_data['state']['economic_indicators']:
                econ_changes[indicator] = market2_data['state']['economic_indicators'][indicator] - market1_data['state']['economic_indicators'][indicator]

        comparison['economic_changes'] = econ_changes

        return comparison