"""
Unit tests for the Market module.
Tests market creation, demand calculation, pricing, competitor AI, and trend analysis.
"""

import pytest
from modules.core.market import (
    Market, MarketState, DemandCalculator, PricingEngine, CompetitorAI, TrendAnalyzer
)


class TestMarketState:
    """Test MarketState dataclass."""

    def test_market_state_creation(self):
        """Test creating MarketState with default values."""
        state = MarketState()
        assert state.demand_level == 1000.0
        assert state.price_index == 1.0
        assert state.competition_intensity == 0.5
        assert isinstance(state.economic_indicators, dict)
        assert len(state.active_events) == 0

    def test_market_state_custom_values(self):
        """Test creating MarketState with custom values."""
        economic_indicators = {'gdp_growth': 0.03, 'inflation': 0.02}
        state = MarketState(
            demand_level=1500.0,
            price_index=1.1,
            competition_intensity=0.7,
            economic_indicators=economic_indicators
        )
        assert state.demand_level == 1500.0
        assert state.price_index == 1.1
        assert state.competition_intensity == 0.7
        assert state.economic_indicators['gdp_growth'] == 0.03


class TestDemandCalculator:
    """Test DemandCalculator class."""

    def test_calculate_demand_basic(self):
        """Test basic demand calculation."""
        calculator = DemandCalculator()
        market_state = MarketState(demand_level=1000.0, price_index=1.0)
        company_factors = {'quality': 0.8, 'brand_value': 60.0, 'customer_satisfaction': 0.75}

        demand = calculator.calculate_demand(100.0, market_state, company_factors)

        assert demand > 0
        assert isinstance(demand, float)

    def test_calculate_demand_price_elasticity(self):
        """Test demand calculation with price elasticity."""
        calculator = DemandCalculator(price_elasticity=-1.5)
        market_state = MarketState(demand_level=1000.0)

        # Higher price should reduce demand
        demand_high = calculator.calculate_demand(120.0, market_state, {})
        demand_low = calculator.calculate_demand(80.0, market_state, {})

        assert demand_low > demand_high

    def test_calculate_economic_multiplier(self):
        """Test economic multiplier calculation."""
        calculator = DemandCalculator()
        market_state = MarketState(
            economic_indicators={
                'gdp_growth': 0.03,
                'inflation': 0.02,
                'interest_rate': 0.04
            }
        )

        multiplier = calculator._calculate_economic_multiplier(market_state)
        assert multiplier > 1.0  # Positive economic indicators should increase demand

    def test_calculate_company_effect(self):
        """Test company-specific demand effects."""
        calculator = DemandCalculator()
        company_factors = {
            'quality': 0.9,
            'brand_value': 80.0,
            'customer_satisfaction': 0.85
        }

        effect = calculator._calculate_company_effect(company_factors)
        assert effect > 1.0  # Good company factors should increase demand


class TestPricingEngine:
    """Test PricingEngine class."""

    def test_calculate_optimal_price(self):
        """Test optimal price calculation."""
        engine = PricingEngine(base_price=100.0)
        market_state = MarketState(competition_intensity=0.5, demand_level=1000.0)
        competitor_prices = [95.0, 105.0, 98.0]
        company_costs = 70.0

        price = engine.calculate_optimal_price(market_state, competitor_prices, company_costs)

        assert price > 0
        assert isinstance(price, float)
        assert len(engine.price_history) == 1

    def test_get_price_trend(self):
        """Test price trend calculation."""
        engine = PricingEngine()

        # Add some price history
        for i in range(10):
            engine.price_history.append(100.0 + i)

        trend = engine.get_price_trend()
        assert isinstance(trend, float)
        assert trend > 0  # Should be positive trend


class TestCompetitorAI:
    """Test CompetitorAI class."""

    def test_competitor_creation(self):
        """Test creating competitors."""
        ai = CompetitorAI(num_competitors=3)

        assert len(ai.competitors) == 3
        for competitor in ai.competitors:
            assert 'id' in competitor
            assert 'name' in competitor
            assert 'strategy' in competitor
            assert 'market_share' in competitor
            assert 'price' in competitor

    def test_update_competitor_actions(self):
        """Test updating competitor actions."""
        ai = CompetitorAI(num_competitors=2)
        market_state = MarketState(competition_intensity=0.6)

        actions = ai.update_competitor_actions(market_state, 100.0, 0.15)

        assert 'competitor_actions' in actions
        assert 'market_impacts' in actions
        assert len(actions['competitor_actions']) == 2

    def test_get_competitor_prices(self):
        """Test getting competitor prices."""
        ai = CompetitorAI(num_competitors=3)
        prices = ai.get_competitor_prices()

        assert len(prices) == 3
        assert all(isinstance(price, float) for price in prices)

    def test_get_competitor_summary(self):
        """Test getting competitor summary."""
        ai = CompetitorAI(num_competitors=2)
        summary = ai.get_competitor_summary()

        assert len(summary) == 2
        for comp in summary:
            assert 'id' in comp
            assert 'name' in comp
            assert 'strategy' in comp
            assert 'market_share' in comp
            assert 'price' in comp
            assert 'quality' in comp


class TestTrendAnalyzer:
    """Test TrendAnalyzer class."""

    def test_trend_analyzer_creation(self):
        """Test creating trend analyzer."""
        analyzer = TrendAnalyzer()
        assert len(analyzer.trend_history) == 0
        assert len(analyzer.seasonal_patterns) == 12  # 12 months

    def test_update_trends(self):
        """Test updating market trends."""
        analyzer = TrendAnalyzer()
        market_state = MarketState()

        analyzer.update_trends(1, market_state)  # Round 1

        assert len(analyzer.trend_history) == 1
        assert market_state.trend_factors['seasonal'] is not None
        assert market_state.trend_factors['trend'] is not None
        assert market_state.trend_factors['cyclical'] is not None

    def test_predict_future_trends(self):
        """Test predicting future trends."""
        analyzer = TrendAnalyzer()

        # Add some history
        market_state = MarketState()
        for round_num in range(1, 4):
            analyzer.update_trends(round_num, market_state)

        predictions = analyzer.predict_future_trends(2)

        assert len(predictions) == 2
        for pred in predictions:
            assert 'seasonal' in pred
            assert 'trend' in pred
            assert 'cyclical' in pred

    def test_get_trend_summary(self):
        """Test getting trend summary."""
        analyzer = TrendAnalyzer()

        # No history
        summary = analyzer.get_trend_summary()
        assert summary['status'] == 'no_trend_data'

        # Add some history
        market_state = MarketState()
        analyzer.update_trends(1, market_state)

        summary = analyzer.get_trend_summary()
        assert 'current_seasonal' in summary
        assert 'current_trend' in summary
        assert 'current_cyclical' in summary
        assert 'trend_direction' in summary


class TestMarket:
    """Test Market class."""

    def test_market_creation(self, sample_market):
        """Test creating a market."""
        assert sample_market.round_number == 0
        assert sample_market.state.demand_level == 1000.0
        assert sample_market.state.price_index == 1.0
        assert sample_market.state.competition_intensity == 0.5

    def test_calculate_demand(self, sample_market):
        """Test demand calculation through market."""
        conditions = {
            'company_factors': {
                'quality': 0.8,
                'brand_value': 60.0,
                'customer_satisfaction': 0.75
            }
        }

        demand = sample_market.calculate_demand(100.0, conditions)
        assert demand > 0
        assert isinstance(demand, float)

    def test_update_competitor_actions(self, sample_market):
        """Test updating competitor actions through market."""
        actions = sample_market.update_competitor_actions()
        assert 'competitor_actions' in actions
        assert 'market_impacts' in actions

    def test_apply_market_event(self, sample_market):
        """Test applying market events."""
        initial_demand = sample_market.state.demand_level
        initial_price = sample_market.state.price_index

        event = {
            'impacts': {
                'demand_change': 0.1,  # +10% demand
                'price_change': -0.05  # -5% price index
            }
        }

        sample_market.apply_market_event(event)

        assert sample_market.state.demand_level == initial_demand * 1.1
        assert sample_market.state.price_index == initial_price * 0.95

    def test_advance_round(self, sample_market):
        """Test advancing market to next round."""
        initial_round = sample_market.round_number

        sample_market.advance_round(1)

        assert sample_market.round_number == 1
        assert len(sample_market.trend_analyzer.trend_history) > 0

    def test_get_market_state(self, sample_market):
        """Test getting market state."""
        state = sample_market.get_market_state()
        assert isinstance(state, MarketState)
        assert state.demand_level == sample_market.state.demand_level

    def test_get_market_summary(self, sample_market):
        """Test getting market summary."""
        summary = sample_market.get_market_summary()

        required_keys = [
            'demand_level', 'price_index', 'competition_intensity',
            'economic_indicators', 'trend_factors', 'active_events',
            'competitors', 'trend_analysis', 'round_number'
        ]

        for key in required_keys:
            assert key in summary

    def test_to_dict_and_from_dict(self, sample_market):
        """Test market serialization."""
        # Convert to dict
        data = sample_market.to_dict()

        assert 'config' in data
        assert 'state' in data
        assert 'round_number' in data
        assert 'competitors' in data

        # Create new market from dict
        new_market = Market.from_dict(data)

        assert new_market.round_number == sample_market.round_number
        assert new_market.state.demand_level == sample_market.state.demand_level
        assert len(new_market.competitor_ai.competitors) == len(sample_market.competitor_ai.competitors)

    def test_market_with_custom_config(self):
        """Test market with custom configuration."""
        config = {
            'initial_demand': 2000.0,
            'initial_price_index': 1.2,
            'competition_intensity': 0.8,
            'base_price': 150.0,
            'num_competitors': 5,
            'price_elasticity': -2.0
        }

        market = Market(config)

        assert market.state.demand_level == 2000.0
        assert market.state.price_index == 1.2
        assert market.state.competition_intensity == 0.8
        assert len(market.competitor_ai.competitors) == 5
        assert market.demand_calculator.price_elasticity == -2.0