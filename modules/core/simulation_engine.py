import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .simulation_state import SimulationState
from .round_manager import RoundManager
from .event_manager import EventManager, Event
from .company import Company, FinancialData, OperationsData, ResourceData, MarketData
from .market import Market, MarketState


@dataclass
class SimulationConfig:
    """Configuration for the simulation engine."""
    max_rounds: int = 10
    num_competitors: int = 3
    initial_market_demand: float = 1000.0
    market_volatility: float = 0.1
    event_frequency: float = 0.3


class SimulationEngine:
    """Main simulation engine that orchestrates the simulation flow."""

    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.round_manager = RoundManager(self.config.max_rounds)
        self.event_manager = EventManager()
        self.current_state: Optional[SimulationState] = None
        self.simulation_history: list = []

    def initialize_simulation(self, scenario: str = "default") -> SimulationState:
        """Initialize a new simulation with the given scenario.

        Args:
            scenario: Scenario name to load initial conditions

        Returns:
            Initial simulation state
        """
        # Reset managers
        self.round_manager.reset()
        self.event_manager.reset()
        self.simulation_history.clear()

        # Create initial simulation state
        player_company = self._create_initial_company()
        initial_state = SimulationState(
            round_number=0,
            player_company=player_company,
            market=self._create_initial_market(),
            competitors=self._create_initial_competitors(),
            events=[],
            kpis=self._calculate_initial_kpis(player_company)
        )

        self.current_state = initial_state
        self.simulation_history.append(initial_state.to_dict())

        return initial_state

    def run_round(self, player_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete round with player decisions.

        Args:
            player_decisions: Dictionary of player decisions for the round

        Returns:
            Round results including updated state and KPIs
        """
        if not self.current_state:
            raise ValueError("Simulation not initialized. Call initialize_simulation() first.")

        # Advance to next round
        new_round = self.round_manager.advance_round()

        # Process player decisions
        processed_decisions = self.round_manager.process_decisions(player_decisions)

        # Generate and trigger events
        random_events = self.event_manager.generate_random_events(new_round)
        scheduled_events = self.event_manager.process_scheduled_events(new_round)

        triggered_events = []
        for event in random_events + scheduled_events:
            event_data = self.event_manager.trigger_event(event, new_round)
            triggered_events.append(event_data)

        # Process active events and get their impacts
        expired_events = self.event_manager.process_active_events()
        event_impacts = self.event_manager.get_active_event_impacts()

        # Advance market to new round
        self.current_state.market.advance_round(new_round)

        # Calculate round results
        round_results = self.round_manager.calculate_round_results(
            self.current_state, processed_decisions
        )

        # Apply event impacts to results
        self._apply_event_impacts(round_results, event_impacts)

        # Apply market events to market
        for event in triggered_events:
            if event.get('type') == 'market_event':
                self.current_state.market.apply_market_event(event)

        # Update simulation state
        self._update_simulation_state(round_results, triggered_events)

        # Store in history
        self.simulation_history.append(self.current_state.to_dict())

        # Create a clean game state dict for return
        game_state_dict = self.current_state.to_dict()
        # Ensure market is properly serialized
        if isinstance(self.current_state.market, dict):
            game_state_dict['market'] = self.current_state.market
        else:
            game_state_dict['market'] = self.current_state.market.to_dict()

        return {
            'round_number': new_round,
            'round_results': round_results,
            'triggered_events': triggered_events,
            'expired_events': expired_events,
            'game_state': game_state_dict,
            'is_simulation_over': self.round_manager.is_simulation_over()
        }

    def get_current_state(self) -> Optional[SimulationState]:
        """Get the current simulation state."""
        return self.current_state

    def save_simulation(self, filename: str) -> bool:
        """Save the current simulation state to a file.

        Args:
            filename: Name of the save file

        Returns:
            True if save was successful
        """
        if not self.current_state:
            return False

        try:
            save_data = {
                'config': {
                    'max_rounds': self.config.max_rounds,
                    'num_competitors': self.config.num_competitors,
                    'initial_market_demand': self.config.initial_market_demand,
                    'market_volatility': self.config.market_volatility,
                    'event_frequency': self.config.event_frequency
                },
                'current_state': self.current_state.to_dict(),
                'round_manager': {
                    'current_round': self.round_manager.current_round,
                    'max_rounds': self.round_manager.max_rounds
                },
                'event_manager': {
                    'active_events': self.event_manager.get_active_events(),
                    'event_history': self.event_manager.get_event_history()
                },
                'market': self.current_state.market.to_dict(),
                'simulation_history': self.simulation_history
            }

            # Ensure data directory exists
            os.makedirs('data/saves', exist_ok=True)

            with open(f'data/saves/{filename}.json', 'w') as f:
                json.dump(save_data, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error saving simulation: {e}")
            return False

    def load_simulation(self, filename: str) -> Optional[SimulationState]:
        """Load a simulation state from a file.

        Args:
            filename: Name of the save file

        Returns:
            Loaded simulation state or None if loading failed
        """
        try:
            with open(f'data/saves/{filename}.json', 'r') as f:
                save_data = json.load(f)

            # Restore configuration
            config_data = save_data.get('config', {})
            self.config = SimulationConfig(**config_data)

            # Restore managers
            round_data = save_data.get('round_manager', {})
            self.round_manager = RoundManager(round_data.get('max_rounds', 10))
            self.round_manager.current_round = round_data.get('current_round', 0)

            self.event_manager = EventManager()
            # Restore active events
            for event_data in save_data.get('event_manager', {}).get('active_events', []):
                self.event_manager.active_events.append(event_data)
            # Restore event history
            for history_item in save_data.get('event_manager', {}).get('event_history', []):
                self.event_manager.event_history.append(history_item)

            # Restore simulation state
            state_data = save_data.get('state_data', save_data.get('current_state'))
            self.current_state = SimulationState.from_dict(state_data)

            # Restore market if available
            if 'market' in save_data:
                self.current_state.market = Market.from_dict(save_data['market'])

            # Restore history
            self.simulation_history = save_data.get('simulation_history', save_data.get('game_history', []))

            return self.current_state
        except Exception as e:
            print(f"Error loading simulation: {e}")
            return None

    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current simulation."""
        if not self.current_state:
            return {'status': 'no_active_simulation'}

        return {
            'current_round': self.round_manager.get_current_round(),
            'max_rounds': self.config.max_rounds,
            'is_simulation_over': self.round_manager.is_simulation_over(),
            'total_events': len(self.event_manager.get_event_history()),
            'active_events': len(self.event_manager.get_active_events()),
            'kpis': self.current_state.kpis,
            'simulation_history_length': len(self.simulation_history)
        }

    def _create_initial_company(self) -> Company:
        """Create initial player company object."""
        financial_data = FinancialData(
            revenue=100000.0,
            costs=80000.0,
            profit=20000.0,
            cash=50000.0,
            assets=200000.0,
            liabilities=150000.0
        )

        operations_data = OperationsData(
            capacity=1000.0,
            efficiency=0.8,
            quality=0.75,
            customer_satisfaction=0.7
        )

        resource_data = ResourceData(
            employees=100,
            equipment=100000.0,
            inventory=50000.0
        )

        market_data = MarketData(
            market_share=0.15,
            brand_value=50.0,
            competitive_position=0.5
        )

        return Company(
            id='player_company',
            name='Player Company',
            financial_data=financial_data,
            operations_data=operations_data,
            resource_data=resource_data,
            market_data=market_data
        )

    def _create_initial_market(self) -> Market:
        """Create initial market object."""
        market_config = {
            'initial_demand': self.config.initial_market_demand,
            'initial_price_index': 1.0,
            'competition_intensity': 0.5,
            'base_price': 100.0,
            'num_competitors': self.config.num_competitors,
            'price_elasticity': -1.5
        }
        return Market(market_config)

    def _create_initial_competitors(self) -> list:
        """Create initial competitor companies."""
        competitors = []
        for i in range(self.config.num_competitors):
            competitor = {
                'id': f'competitor_{i+1}',
                'name': f'Competitor Company {i+1}',
                'market_share': 0.25 / self.config.num_competitors,
                'aggressiveness': 0.5 + (i * 0.1),  # Varying strategies
                'financials': {
                    'revenue': 80000.0 + (i * 10000.0),
                    'profit': 15000.0 + (i * 2000.0)
                }
            }
            competitors.append(competitor)
        return competitors

    def _calculate_initial_kpis(self, company: Company) -> Dict[str, float]:
        """Calculate initial KPI values from company object."""
        return company.get_kpis()

    def _apply_event_impacts(self, round_results: Dict[str, Any], event_impacts: Dict[str, float]):
        """Apply event impacts to round results."""
        for metric, impact in event_impacts.items():
            if metric in round_results:
                if metric in ['revenue', 'costs', 'profit']:
                    # Percentage impact on financial metrics
                    round_results[metric] *= (1.0 + impact)
                elif metric in ['market_share', 'customer_satisfaction']:
                    # Direct additive impact on percentages
                    round_results[metric] = max(0.0, min(1.0, round_results[metric] + impact))
                else:
                    # Generic percentage impact
                    round_results[metric] *= (1.0 + impact)

    def _apply_round_results_to_company(self, round_results: Dict[str, Any]):
        """Apply round results to company state."""
        company = self.current_state.player_company

        # Update financial results if provided
        if 'revenue' in round_results:
            company.financial_data.revenue = round_results['revenue']
        if 'costs' in round_results:
            company.financial_data.costs = round_results['costs']
        if 'profit' in round_results:
            company.financial_data.profit = round_results['profit']

        # Update market position
        if 'market_share' in round_results:
            company.market_data.market_share = round_results['market_share']
        if 'customer_satisfaction' in round_results:
            company.operations_data.customer_satisfaction = round_results['customer_satisfaction']

    def _update_simulation_state(self, round_results: Dict[str, Any], triggered_events: list):
        """Update the current simulation state with round results."""
        if not self.current_state:
            return

        # Update round number
        self.current_state.round_number = self.round_manager.get_current_round()

        # Update company state with market conditions
        market_state = self.current_state.market.get_market_state()
        market_conditions = {
            'demand_level': market_state.demand_level,
            'price_index': market_state.price_index,
            'market_price': 100.0,  # Base market price
            'economic_indicators': market_state.economic_indicators,
            'competition_intensity': market_state.competition_intensity
        }

        # Apply round results to company
        self._apply_round_results_to_company(round_results)

        # Update company state based on market conditions
        self.current_state.player_company.update_state(market_conditions)

        # Update events
        self.current_state.events = [event['event'] for event in triggered_events]

        # Update KPIs from company
        self.current_state.kpis = self.current_state.player_company.get_kpis()