from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import math


@dataclass
class MarketState:
    """Represents the current state of the market."""
    demand_level: float = 1000.0
    price_index: float = 1.0
    competition_intensity: float = 0.5
    economic_indicators: Dict[str, float] = field(default_factory=lambda: {
        'gdp_growth': 0.02,
        'inflation': 0.03,
        'interest_rate': 0.05
    })
    active_events: List[Dict[str, Any]] = field(default_factory=list)
    trend_factors: Dict[str, float] = field(default_factory=lambda: {
        'seasonal': 0.0,
        'trend': 0.0,
        'cyclical': 0.0
    })


class DemandCalculator:
    """Calculates market demand based on various factors."""

    def __init__(self, base_demand: float = 1000.0, price_elasticity: float = -1.5):
        self.base_demand = base_demand
        self.price_elasticity = price_elasticity  # Price elasticity of demand

    def calculate_demand(self, price: float, market_state: MarketState,
                        company_factors: Dict[str, Any]) -> float:
        """Calculate market demand considering price, market conditions, and company factors.

        Args:
            price: Current market price
            market_state: Current market state
            company_factors: Company-specific factors (quality, brand, etc.)

        Returns:
            Calculated demand level
        """
        # Base demand adjusted for economic conditions
        economic_multiplier = self._calculate_economic_multiplier(market_state)

        # Price effect using elasticity
        base_price = 100.0  # Reference price
        price_effect = (price / base_price) ** self.price_elasticity

        # Market trend effects
        trend_effect = self._calculate_trend_effect(market_state)

        # Company-specific factors
        company_effect = self._calculate_company_effect(company_factors)

        # Seasonal and cyclical effects
        seasonal_effect = 1.0 + market_state.trend_factors['seasonal']
        cyclical_effect = 1.0 + market_state.trend_factors['cyclical']

        # Calculate final demand
        demand = (self.base_demand * economic_multiplier * price_effect *
                 trend_effect * company_effect * seasonal_effect * cyclical_effect)

        # Apply competition intensity (higher competition reduces demand)
        competition_effect = 1.0 - (market_state.competition_intensity * 0.2)
        demand *= competition_effect

        # Ensure non-negative demand
        return max(0.0, demand)

    def _calculate_economic_multiplier(self, market_state: MarketState) -> float:
        """Calculate multiplier based on economic indicators."""
        gdp_effect = 1.0 + market_state.economic_indicators['gdp_growth']
        inflation_effect = 1.0 - (market_state.economic_indicators['inflation'] * 0.5)
        interest_effect = 1.0 - (market_state.economic_indicators['interest_rate'] * 0.3)

        return gdp_effect * inflation_effect * interest_effect

    def _calculate_trend_effect(self, market_state: MarketState) -> float:
        """Calculate trend-based demand multiplier."""
        return 1.0 + market_state.trend_factors['trend']

    def _calculate_company_effect(self, company_factors: Dict[str, Any]) -> float:
        """Calculate company-specific demand effects."""
        quality_effect = 1.0 + (company_factors.get('quality', 0.75) - 0.75) * 0.5
        brand_effect = 1.0 + (company_factors.get('brand_value', 50.0) / 100.0) * 0.3
        satisfaction_effect = 1.0 + (company_factors.get('customer_satisfaction', 0.7) - 0.7) * 0.4

        return quality_effect * brand_effect * satisfaction_effect


class PricingEngine:
    """Handles dynamic pricing and price optimization."""

    def __init__(self, base_price: float = 100.0):
        self.base_price = base_price
        self.price_history: List[float] = []

    def calculate_optimal_price(self, market_state: MarketState,
                               competitor_prices: List[float],
                               company_costs: float) -> float:
        """Calculate optimal price considering market conditions and competitors.

        Args:
            market_state: Current market state
            competitor_prices: List of competitor prices
            company_costs: Company's cost structure

        Returns:
            Recommended price
        """
        # Cost-plus pricing as baseline
        cost_plus_price = company_costs * 1.3  # 30% margin

        # Market-based pricing
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else self.base_price
        market_price = avg_competitor_price * (1.0 + market_state.competition_intensity * 0.1)

        # Demand-responsive pricing
        demand_multiplier = 1.0 + (market_state.demand_level / 1000.0 - 1.0) * 0.2

        # Economic condition adjustment
        economic_adjustment = 1.0 + market_state.economic_indicators['inflation']

        # Calculate optimal price
        optimal_price = (cost_plus_price * 0.4 + market_price * 0.4 + self.base_price * demand_multiplier * 0.2) * economic_adjustment

        # Record in history
        self.price_history.append(optimal_price)
        if len(self.price_history) > 10:
            self.price_history.pop(0)

        return optimal_price

    def get_price_trend(self) -> float:
        """Get recent price trend (positive = increasing)."""
        if len(self.price_history) < 2:
            return 0.0

        recent_prices = self.price_history[-5:] if len(self.price_history) >= 5 else self.price_history
        if len(recent_prices) < 2:
            return 0.0

        # Calculate trend using linear regression slope
        n = len(recent_prices)
        x = list(range(n))
        y = recent_prices

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0

        return slope


class CompetitorAI:
    """AI system for managing competitor behavior."""

    def __init__(self, num_competitors: int = 3):
        self.num_competitors = num_competitors
        self.competitors: List[Dict[str, Any]] = []
        self._initialize_competitors()

    def _initialize_competitors(self):
        """Initialize competitor profiles with different strategies."""
        strategies = [
            {'name': 'Cost_Leader', 'aggressiveness': 0.8, 'price_sensitivity': 0.9, 'innovation_focus': 0.3},
            {'name': 'Quality_Focused', 'aggressiveness': 0.5, 'price_sensitivity': 0.6, 'innovation_focus': 0.8},
            {'name': 'Balanced', 'aggressiveness': 0.6, 'price_sensitivity': 0.7, 'innovation_focus': 0.5}
        ]

        for i in range(self.num_competitors):
            strategy = strategies[i % len(strategies)]
            competitor = {
                'id': f'competitor_{i+1}',
                'name': f'Competitor Company {i+1}',
                'strategy': strategy['name'],
                'aggressiveness': strategy['aggressiveness'] + random.uniform(-0.1, 0.1),
                'price_sensitivity': strategy['price_sensitivity'] + random.uniform(-0.1, 0.1),
                'innovation_focus': strategy['innovation_focus'] + random.uniform(-0.1, 0.1),
                'market_share': 0.25 / self.num_competitors,
                'price': 100.0,
                'quality': 0.7 + random.uniform(-0.1, 0.1),
                'last_decision': None
            }
            self.competitors.append(competitor)

    def update_competitor_actions(self, market_state: MarketState,
                                 player_price: float, player_market_share: float) -> Dict[str, Any]:
        """Update competitor actions based on market conditions and player behavior.

        Args:
            market_state: Current market state
            player_price: Player's current price
            player_market_share: Player's current market share

        Returns:
            Dictionary of competitor actions and market impacts
        """
        actions = {}
        total_market_impact = {'price_pressure': 0.0, 'quality_competition': 0.0, 'market_share_shift': 0.0}

        for competitor in self.competitors:
            action = self._decide_competitor_action(competitor, market_state, player_price, player_market_share)
            actions[competitor['id']] = action

            # Accumulate market impacts
            total_market_impact['price_pressure'] += action.get('price_change', 0.0) * competitor['market_share']
            total_market_impact['quality_competition'] += action.get('quality_change', 0.0) * competitor['innovation_focus']
            total_market_impact['market_share_shift'] += action.get('aggressive_move', 0.0) * competitor['aggressiveness']

        # Apply actions to competitors
        self._apply_competitor_actions(actions)

        return {
            'competitor_actions': actions,
            'market_impacts': total_market_impact
        }

    def _decide_competitor_action(self, competitor: Dict[str, Any],
                                 market_state: MarketState, player_price: float,
                                 player_market_share: float) -> Dict[str, Any]:
        """Decide what action a competitor should take."""
        action = {'price_change': 0.0, 'quality_change': 0.0, 'aggressive_move': 0.0}

        # Price response based on strategy
        price_gap = player_price - competitor['price']
        if abs(price_gap) > 5.0:  # Significant price difference
            if competitor['price_sensitivity'] > 0.7:  # Price-sensitive competitor
                action['price_change'] = -price_gap * 0.3 * competitor['aggressiveness']
            elif competitor['strategy'] == 'Cost_Leader':
                action['price_change'] = -price_gap * 0.5  # Aggressive price matching

        # Quality improvement decisions
        if competitor['innovation_focus'] > 0.6 and random.random() < 0.2:  # 20% chance
            action['quality_change'] = 0.05 * competitor['innovation_focus']

        # Market share defense
        if player_market_share > competitor['market_share'] * 1.2:  # Player gaining significantly
            action['aggressive_move'] = 0.1 * competitor['aggressiveness']

        competitor['last_decision'] = action
        return action

    def _apply_competitor_actions(self, actions: Dict[str, Dict[str, Any]]):
        """Apply decided actions to competitor states."""
        for comp_id, action in actions.items():
            competitor = next(c for c in self.competitors if c['id'] == comp_id)

            # Update price
            competitor['price'] += action.get('price_change', 0.0)

            # Update quality
            competitor['quality'] = min(1.0, competitor['quality'] + action.get('quality_change', 0.0))

            # Update market share based on actions
            share_change = action.get('aggressive_move', 0.0) * 0.02  # Small share changes
            competitor['market_share'] = max(0.01, min(0.5, competitor['market_share'] + share_change))

    def get_competitor_prices(self) -> List[float]:
        """Get current competitor prices."""
        return [comp['price'] for comp in self.competitors]

    def get_competitor_summary(self) -> List[Dict[str, Any]]:
        """Get summary of competitor states."""
        return [{
            'id': comp['id'],
            'name': comp['name'],
            'strategy': comp['strategy'],
            'market_share': comp['market_share'],
            'price': comp['price'],
            'quality': comp['quality']
        } for comp in self.competitors]


class TrendAnalyzer:
    """Analyzes and simulates market trends over time."""

    def __init__(self):
        self.trend_history: List[Dict[str, float]] = []
        self.seasonal_patterns = self._generate_seasonal_patterns()

    def _generate_seasonal_patterns(self) -> Dict[int, float]:
        """Generate seasonal demand patterns (12 months)."""
        # Simplified seasonal pattern: higher in Q4, lower in Q1
        return {
            1: -0.1, 2: -0.15, 3: -0.05, 4: 0.0,
            5: 0.05, 6: 0.1, 7: 0.15, 8: 0.1,
            9: 0.05, 10: 0.0, 11: 0.1, 12: 0.2
        }

    def update_trends(self, round_number: int, market_state: MarketState):
        """Update market trends for the current round."""
        # Seasonal component
        month = (round_number % 12) + 1
        seasonal = self.seasonal_patterns.get(month, 0.0)

        # Trend component (gradual changes)
        trend = self._calculate_trend_component(round_number)

        # Cyclical component (business cycles)
        cyclical = self._calculate_cyclical_component(round_number)

        # Update market state
        market_state.trend_factors['seasonal'] = seasonal
        market_state.trend_factors['trend'] = trend
        market_state.trend_factors['cyclical'] = cyclical

        # Record in history
        self.trend_history.append({
            'round': round_number,
            'seasonal': seasonal,
            'trend': trend,
            'cyclical': cyclical
        })

        # Keep last 24 rounds
        if len(self.trend_history) > 24:
            self.trend_history.pop(0)

    def _calculate_trend_component(self, round_number: int) -> float:
        """Calculate long-term trend component."""
        # Simulate gradual market growth or decline
        base_trend = 0.005  # 0.5% growth per round
        volatility = random.uniform(-0.01, 0.01)
        return base_trend + volatility

    def _calculate_cyclical_component(self, round_number: int) -> float:
        """Calculate cyclical component (business cycles)."""
        # Simplified 8-round business cycle
        cycle_position = round_number % 8
        cycle_effects = {
            0: 0.05, 1: 0.03, 2: 0.01, 3: -0.01,
            4: -0.03, 5: -0.05, 6: -0.03, 7: 0.01
        }
        return cycle_effects.get(cycle_position, 0.0)

    def predict_future_trends(self, rounds_ahead: int = 3) -> List[Dict[str, float]]:
        """Predict future trend values."""
        predictions = []
        current_round = len(self.trend_history)

        for i in range(1, rounds_ahead + 1):
            future_round = current_round + i
            pred_seasonal = self.seasonal_patterns.get((future_round % 12) + 1, 0.0)
            pred_trend = self._calculate_trend_component(future_round)
            pred_cyclical = self._calculate_cyclical_component(future_round)

            predictions.append({
                'round': future_round,
                'seasonal': pred_seasonal,
                'trend': pred_trend,
                'cyclical': pred_cyclical
            })

        return predictions

    def get_trend_summary(self) -> Dict[str, Any]:
        """Get summary of current trends."""
        if not self.trend_history:
            return {'status': 'no_trend_data'}

        latest = self.trend_history[-1]
        return {
            'current_seasonal': latest['seasonal'],
            'current_trend': latest['trend'],
            'current_cyclical': latest['cyclical'],
            'trend_direction': 'growing' if latest['trend'] > 0 else 'declining',
            'seasonal_phase': 'high' if latest['seasonal'] > 0.05 else 'low' if latest['seasonal'] < -0.05 else 'normal'
        }


class Market:
    """Main Market class that orchestrates market dynamics."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.state = MarketState(
            demand_level=self.config.get('initial_demand', 1000.0),
            price_index=self.config.get('initial_price_index', 1.0),
            competition_intensity=self.config.get('competition_intensity', 0.5)
        )

        # Initialize components
        self.demand_calculator = DemandCalculator(
            base_demand=self.state.demand_level,
            price_elasticity=self.config.get('price_elasticity', -1.5)
        )
        self.pricing_engine = PricingEngine(base_price=self.config.get('base_price', 100.0))
        self.competitor_ai = CompetitorAI(num_competitors=self.config.get('num_competitors', 3))
        self.trend_analyzer = TrendAnalyzer()

        self.round_number = 0

    def calculate_demand(self, price: float, conditions: Dict[str, Any]) -> float:
        """Calculate market demand for given price and conditions."""
        company_factors = conditions.get('company_factors', {})
        return self.demand_calculator.calculate_demand(price, self.state, company_factors)

    def update_competitor_actions(self) -> Dict[str, Any]:
        """Update competitor actions and return market impacts."""
        # Get player information from conditions (would be passed in real implementation)
        player_price = 100.0  # Placeholder
        player_market_share = 0.15  # Placeholder

        return self.competitor_ai.update_competitor_actions(
            self.state, player_price, player_market_share
        )

    def apply_market_event(self, event: Dict[str, Any]):
        """Apply a market event's impact to the market state."""
        impacts = event.get('impacts', {})

        # Apply demand impacts
        if 'demand_change' in impacts:
            self.state.demand_level *= (1.0 + impacts['demand_change'])

        # Apply price impacts
        if 'price_change' in impacts:
            self.state.price_index *= (1.0 + impacts['price_change'])

        # Apply competition impacts
        if 'competition_change' in impacts:
            self.state.competition_intensity = max(0.0, min(1.0,
                self.state.competition_intensity + impacts['competition_change']))

        # Apply economic indicator changes
        for indicator, change in impacts.items():
            if indicator in self.state.economic_indicators:
                self.state.economic_indicators[indicator] += change

        # Add to active events
        self.state.active_events.append(event)

    def advance_round(self, round_number: int):
        """Advance the market to the next round."""
        self.round_number = round_number

        # Update trends
        self.trend_analyzer.update_trends(round_number, self.state)

        # Update competitor actions
        competitor_impacts = self.update_competitor_actions()

        # Apply competitor impacts to market state
        impacts = competitor_impacts.get('market_impacts', {})
        self.state.competition_intensity = max(0.0, min(1.0,
            self.state.competition_intensity + impacts.get('price_pressure', 0.0) * 0.1))

    def get_market_state(self) -> MarketState:
        """Get the current market state."""
        return self.state

    def get_competitor_prices(self) -> List[float]:
        """Get current competitor prices."""
        return self.competitor_ai.get_competitor_prices()

    def get_market_summary(self) -> Dict[str, Any]:
        """Get a comprehensive market summary."""
        return {
            'demand_level': self.state.demand_level,
            'price_index': self.state.price_index,
            'competition_intensity': self.state.competition_intensity,
            'economic_indicators': self.state.economic_indicators,
            'trend_factors': self.state.trend_factors,
            'active_events': self.state.active_events,
            'competitors': self.competitor_ai.get_competitor_summary(),
            'trend_analysis': self.trend_analyzer.get_trend_summary(),
            'round_number': self.round_number
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert market to dictionary for serialization."""
        return {
            'config': self.config,
            'state': {
                'demand_level': self.state.demand_level,
                'price_index': self.state.price_index,
                'competition_intensity': self.state.competition_intensity,
                'economic_indicators': self.state.economic_indicators,
                'active_events': self.state.active_events,
                'trend_factors': self.state.trend_factors
            },
            'round_number': self.round_number,
            'competitors': self.competitor_ai.competitors,
            'trend_history': self.trend_analyzer.trend_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Market':
        """Create market from dictionary."""
        market = cls(config=data.get('config', {}))

        # Restore state
        state_data = data.get('state', {})
        market.state = MarketState(**state_data)

        # Restore round number
        market.round_number = data.get('round_number', 0)

        # Restore competitors
        if 'competitors' in data:
            market.competitor_ai.competitors = data['competitors']

        # Restore trend history
        if 'trend_history' in data:
            market.trend_analyzer.trend_history = data['trend_history']

        return market