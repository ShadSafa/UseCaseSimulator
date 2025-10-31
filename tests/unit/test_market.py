import pytest
from modules.core.market import (
    Market, MarketState, DemandCalculator, PricingEngine,
    CompetitorAI, TrendAnalyzer
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
        assert isinstance(state.trend_factors, dict)

    def test_market_state_custom_values(self):
        """Test creating MarketState with custom values."""
        economic_indicators = {'gdp_growth': 0.03, 'inflation': 0.02}
        trend_factors = {'seasonal': 0.1, 'trend': 0.05}

        state = MarketState(
            demand_level=1200.0,
            price_index=1.1,
            competition_intensity=0.7,
            economic_indicators=economic_indicators,
            trend_factors=trend_factors
        )

        assert state.demand_level == 1200.0
        assert state.price_index == 1.1
        assert state.competition_intensity == 0.7
        assert state.economic_indicators == economic_indicators
        assert state.trend_factors == trend_factors


class TestDemandCalculator:
    """Test DemandCalculator class."""

    def test_calculate_demand_basic(self, demand_calculator, sample_market_state, company_factors_high_quality):
        """Test basic demand calculation."""
        demand = demand_calculator.calculate_demand(
            price=100.0,
            market_state=sample_market_state,
            company_factors=company_factors_high_quality
        )

        assert demand > 0
        assert isinstance(demand, float)

    def test_calculate_demand_price_elasticity(self, demand_calculator, sample_market_state, company_factors_high_quality):
        """Test that demand responds to price changes according to elasticity."""
        demand_high_price = demand_calculator.calculate_demand(
            price=120.0,
            market_state=sample_market_state,
            company_factors=company_factors_high_quality
        )

        demand_low_price = demand_calculator.calculate_demand(
            price=80.0,
            market_state=sample_market_state,
            company_factors=company_factors_high_quality
        )

        # Lower price should result in higher demand
        assert demand_low_price > demand_high_price

    def test_calculate_demand_company_factors(self, demand_calculator, sample_market_state):
        """Test that company factors affect demand."""
        high_quality_factors = {
            'quality': 0.9,
            'brand_value': 80.0,
            'customer_satisfaction': 0.85
        }

        low_quality_factors = {
            'quality': 0.4,
            'brand_value': 20.0,
            'customer_satisfaction': 0.5
        }

        demand_high = demand_calculator.calculate_demand(
            price=100.0,
            market_state=sample_market_state,
            company_factors=high_quality_factors
        )

        demand_low = demand_calculator.calculate_demand(
            price=100.0,
            market_state=sample_market_state,
            company_factors=low_quality_factors
        )

        # Higher quality should result in higher demand
        assert demand_high > demand_low

    def test_economic_multiplier(self, demand_calculator, sample_market_state, company_factors_high_quality):
        """Test economic multiplier calculation."""
        multiplier = demand_calculator._calculate_economic_multiplier(sample_market_state)
        assert multiplier > 0
        assert isinstance(multiplier, float)

    def test_trend_effect(self, demand_calculator, sample_market_state):
        """Test trend effect calculation."""
        effect = demand_calculator._calculate_trend_effect(sample_market_state)
        assert isinstance(effect, float)
        assert effect == 1.0 + sample_market_state.trend_factors['trend']


class TestPricingEngine:
    """Test PricingEngine class."""

    def test_calculate_optimal_price(self, pricing_engine, sample_market_state, competitor_prices):
        """Test optimal price calculation."""
        company_costs = 80.0  # Cost per unit

        optimal_price = pricing_engine.calculate_optimal_price(
            market_state=sample_market_state,
            competitor_prices=competitor_prices,
            company_costs=company_costs
        )

        assert optimal_price > 0
        assert isinstance(optimal_price, float)
        assert optimal_price >= company_costs  # Should be at least cost-plus

    def test_price_history_tracking(self, pricing_engine, sample_market_state, competitor_prices):
        """Test that pricing engine tracks price history."""
        initial_history_length = len(pricing_engine.price_history)

        pricing_engine.calculate_optimal_price(
            market_state=sample_market_state,
            competitor_prices=competitor_prices,
            company_costs=80.0
        )

        assert len(pricing_engine.price_history) == initial_history_length + 1

    def test_price_trend_calculation(self, pricing_engine):
        """Test price trend calculation."""
        # Add some historical prices
        pricing_engine.price_history = [100.0, 102.0, 105.0, 103.0, 106.0]

        trend = pricing_engine.get_price_trend()
        assert isinstance(trend, float)

    def test_price_trend_insufficient_data(self, pricing_engine):
        """Test price trend with insufficient data."""
        pricing_engine.price_history = [100.0]  # Only one data point

        trend = pricing_engine.get_price_trend()
        assert trend == 0.0


class TestCompetitorAI:
    """Test CompetitorAI class."""

    def test_competitor_initialization(self, competitor_ai):
        """Test competitor AI initialization."""
        assert len(competitor_ai.competitors) == 3  # Default num_competitors

        for competitor in competitor_ai.competitors:
            assert 'id' in competitor
            assert 'name' in competitor
            assert 'strategy' in competitor
            assert 'market_share' in competitor
            assert 'price' in competitor
            assert 'quality' in competitor

    def test_update_competitor_actions(self, competitor_ai, sample_market_state):
        """Test updating competitor actions."""
        player_price = 100.0
        player_market_share = 0.15

        results = competitor_ai.update_competitor_actions(
            market_state=sample_market_state,
            player_price=player_price,
            player_market_share=player_market_share
        )

        assert 'competitor_actions' in results
        assert 'market_impacts' in results
        assert len(results['competitor_actions']) == 3

    def test_get_competitor_prices(self, competitor_ai):
        """Test getting competitor prices."""
        prices = competitor_ai.get_competitor_prices()
        assert len(prices) == 3
        assert all(isinstance(price, (int, float)) for price in prices)

    def test_get_competitor_summary(self, competitor_ai):
        """Test getting competitor summary."""
        summary = competitor_ai.get_competitor_summary()
        assert len(summary) == 3

        for comp in summary:
            required_fields = ['id', 'name', 'strategy', 'market_share', 'price', 'quality']
            for field in required_fields:
                assert field in comp


class TestTrendAnalyzer:
    """Test TrendAnalyzer class."""

    def test_trend_analyzer_initialization(self, trend_analyzer):
        """Test trend analyzer initialization."""
        assert hasattr(trend_analyzer, 'trend_history')
        assert hasattr(trend_analyzer, 'seasonal_patterns')
        assert len(trend_analyzer.seasonal_patterns) == 12  # 12 months

    def test_update_trends(self, trend_analyzer, sample_market_state):
        """Test updating market trends."""
        initial_history_length = len(trend_analyzer.trend_history)

        trend_analyzer.update_trends(round_number=1, market_state=sample_market_state)

        assert len(trend_analyzer.trend_history) == initial_history_length + 1

        # Check that market state was updated
        assert 'seasonal' in sample_market_state.trend_factors
        assert 'trend' in sample_market_state.trend_factors
        assert 'cyclical' in sample_market_state.trend_factors

    def test_seasonal_patterns(self, trend_analyzer):
        """Test seasonal pattern generation."""
        patterns = trend_analyzer.seasonal_patterns

        assert len(patterns) == 12
        assert all(isinstance(value, float) for value in patterns.values())

        # Check some expected patterns (higher in Q4, lower in Q1)
        assert patterns[12] > patterns[1]  # December > January

    def test_predict_future_trends(self, trend_analyzer, sample_market_state):
        """Test future trend prediction."""
        # Add some historical data
        for round_num in range(1, 4):
            trend_analyzer.update_trends(round_num, sample_market_state)

        predictions = trend_analyzer.predict_future_trends(rounds_ahead=2)

        assert len(predictions) == 2
        for pred in predictions:
            assert 'seasonal' in pred
            assert 'trend' in pred
            assert 'cyclical' in pred

    def test_get_trend_summary_no_data(self, trend_analyzer):
        """Test trend summary with no data."""
        summary = trend_analyzer.get_trend_summary()
        assert summary['status'] == 'no_trend_data'

    def test_get_trend_summary_with_data(self, trend_analyzer, sample_market_state):
        """Test trend summary with data."""
        trend_analyzer.update_trends(1, sample_market_state)

        summary = trend_analyzer.get_trend_summary()

        required_fields = ['current_seasonal', 'current_trend', 'current_cyclical',
                          'trend_direction', 'seasonal_phase']
        for field in required_fields:
            assert field in summary


class TestMarket:
    """Test Market class."""

    def test_market_creation(self, sample_market):
        """Test creating a market."""
        assert sample_market.round_number == 0
        assert hasattr(sample_market, 'state')
        assert hasattr(sample_market, 'demand_calculator')
        assert hasattr(sample_market, 'pricing_engine')
        assert hasattr(sample_market, 'competitor_ai')
        assert hasattr(sample_market, 'trend_analyzer')

    def test_calculate_demand(self, sample_market, company_factors_high_quality):
        """Test market demand calculation."""
        demand = sample_market.calculate_demand(
            price=100.0,
            conditions={'company_factors': company_factors_high_quality}
        )

        assert demand > 0
        assert isinstance(demand, float)

    def test_update_competitor_actions(self, sample_market):
        """Test updating competitor actions through market."""
        results = sample_market.update_competitor_actions()

        assert 'competitor_actions' in results
        assert 'market_impacts' in results

    def test_apply_market_event_demand_change(self, sample_market):
        """Test applying market event that changes demand."""
        initial_demand = sample_market.state.demand_level

        event = {
            'impacts': {'demand_change': 0.1}  # 10% increase
        }

        sample_market.apply_market_event(event)

        expected_demand = initial_demand * 1.1
        assert sample_market.state.demand_level == expected_demand

    def test_apply_market_event_price_change(self, sample_market):
        """Test applying market event that changes price."""
        initial_price_index = sample_market.state.price_index

        event = {
            'impacts': {'price_change': -0.05}  # 5% decrease
        }

        sample_market.apply_market_event(event)

        expected_price = initial_price_index * 0.95
        assert sample_market.state.price_index == expected_price

    def test_apply_market_event_competition_change(self, sample_market):
        """Test applying market event that changes competition."""
        initial_competition = sample_market.state.competition_intensity

        event = {
            'impacts': {'competition_change': 0.2}  # Increase competition
        }

        sample_market.apply_market_event(event)

        expected_competition = min(1.0, initial_competition + 0.2)
        assert sample_market.state.competition_intensity == expected_competition

    def test_apply_market_event_economic_change(self, sample_market):
        """Test applying market event that changes economic indicators."""
        initial_gdp = sample_market.state.economic_indicators['gdp_growth']

        event = {
            'impacts': {'gdp_growth': 0.02}  # Increase GDP growth
        }

        sample_market.apply_market_event(event)

        assert sample_market.state.economic_indicators['gdp_growth'] == initial_gdp + 0.02

    def test_advance_round(self, sample_market):
        """Test advancing market to next round."""
        initial_round = sample_market.round_number

        sample_market.advance_round(2)

        assert sample_market.round_number == 2

        # Check that trends were updated
        assert 'seasonal' in sample_market.state.trend_factors

    def test_get_market_state(self, sample_market):
        """Test getting market state."""
        state = sample_market.get_market_state()

        assert isinstance(state, MarketState)
        assert state.demand_level == sample_market.state.demand_level
        assert state.price_index == sample_market.state.price_index

    def test_get_competitor_prices(self, sample_market):
        """Test getting competitor prices through market."""
        prices = sample_market.get_competitor_prices()
        assert len(prices) == 3  # Default competitors
        assert all(isinstance(price, (int, float)) for price in prices)

    def test_get_market_summary(self, sample_market):
        """Test getting market summary."""
        summary = sample_market.get_market_summary()

        required_fields = [
            'demand_level', 'price_index', 'competition_intensity',
            'economic_indicators', 'trend_factors', 'competitors',
            'trend_analysis', 'round_number'
        ]

        for field in required_fields:
            assert field in summary

    def test_to_dict(self, sample_market):
        """Test converting market to dictionary."""
        data = sample_market.to_dict()

        assert 'config' in data
        assert 'state' in data
        assert 'round_number' in data
        assert 'competitors' in data
        assert 'trend_history' in data

    def test_from_dict(self, sample_market):
        """Test creating market from dictionary."""
        data = sample_market.to_dict()
        new_market = Market.from_dict(data)

        assert new_market.round_number == sample_market.round_number
        assert new_market.state.demand_level == sample_market.state.demand_level
        assert len(new_market.competitor_ai.competitors) == len(sample_market.competitor_ai.competitors)