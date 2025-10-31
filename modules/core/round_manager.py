from typing import Dict, Any, Optional
from .simulation_state import SimulationState


class RoundManager:
    """Manages round progression and decision processing."""

    def __init__(self, max_rounds: int = 10):
        self.max_rounds = max_rounds
        self.current_round = 0

    def advance_round(self) -> int:
        """Advance to the next round. Returns the new round number."""
        if self.current_round < self.max_rounds:
            self.current_round += 1
        return self.current_round

    def process_decisions(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Process player decisions for the current round.

        Args:
            decisions: Dictionary of player decisions

        Returns:
            Processed decision results
        """
        # Placeholder for decision processing logic
        processed_results = {
            'decisions_processed': len(decisions),
            'round': self.current_round,
            'results': {}
        }

        # Basic validation and processing
        for decision_type, params in decisions.items():
            if decision_type == 'pricing':
                processed_results['results']['pricing'] = self._process_pricing_decision(params)
            elif decision_type == 'investment':
                processed_results['results']['investment'] = self._process_investment_decision(params)
            elif decision_type == 'marketing':
                processed_results['results']['marketing'] = self._process_marketing_decision(params)
            else:
                processed_results['results'][decision_type] = {'status': 'unknown_decision_type'}

        return processed_results

    def calculate_round_results(self, simulation_state: SimulationState, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate results for the current round based on decisions and market conditions.

        Args:
            simulation_state: Current simulation state
            decisions: Player decisions

        Returns:
            Round results including KPIs and state changes
        """
        results = {
            'round': self.current_round,
            'revenue': 0.0,
            'costs': 0.0,
            'profit': 0.0,
            'market_share': 0.0,
            'customer_satisfaction': 0.0,
            'summary': f"Round {self.current_round} completed"
        }

        # Placeholder calculations - will be enhanced with actual business logic
        base_revenue = 100000.0
        base_costs = 80000.0

        # Apply decision impacts (simplified)
        if 'pricing' in decisions.get('results', {}):
            price_multiplier = decisions['results']['pricing'].get('impact', 1.0)
            results['revenue'] = base_revenue * price_multiplier

        if 'marketing' in decisions.get('results', {}):
            marketing_impact = decisions['results']['marketing'].get('impact', 0.0)
            results['revenue'] *= (1.0 + marketing_impact)

        results['costs'] = base_costs
        results['profit'] = results['revenue'] - results['costs']
        results['market_share'] = 0.15  # Placeholder
        results['customer_satisfaction'] = 0.75  # Placeholder

        return results

    def is_simulation_over(self) -> bool:
        """Check if the simulation has reached its maximum rounds."""
        return self.current_round >= self.max_rounds

    def get_current_round(self) -> int:
        """Get the current round number."""
        return self.current_round

    def reset(self):
        """Reset the round manager to initial state."""
        self.current_round = 0

    def _process_pricing_decision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process pricing decision."""
        price = params.get('price', 100.0)
        # Simple impact calculation
        impact = max(0.5, min(1.5, price / 100.0))
        return {
            'price': price,
            'impact': impact,
            'description': f"Pricing set to ${price:.2f}"
        }

    def _process_investment_decision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process investment decision."""
        amount = params.get('amount', 0.0)
        return {
            'amount': amount,
            'impact': amount * 0.1,  # 10% efficiency improvement per unit invested
            'description': f"Invested ${amount:.2f} in operations"
        }

    def _process_marketing_decision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process marketing decision."""
        budget = params.get('budget', 0.0)
        return {
            'budget': budget,
            'impact': min(0.5, budget / 10000.0),  # Max 50% revenue increase
            'description': f"Marketing budget: ${budget:.2f}"
        }