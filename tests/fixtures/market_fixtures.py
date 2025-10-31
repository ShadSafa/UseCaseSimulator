import pytest
from modules.core.market import (
    Market, MarketState, DemandCalculator, PricingEngine,
    CompetitorAI, TrendAnalyzer
)


@pytest.fixture
def sample_market_state():
    """Create sample market state for testing."""
    return MarketState(
        demand_level=1000.0,
        price_index=1.0,
        competition_intensity=0.5,
        economic_indicators={
            'gdp_growth': 0.02,
            'inflation': 0.03,
            'interest_rate': 0.05
        },
        trend_factors={
            'seasonal': 0.0,
            'trend': 0.0,
            'cyclical': 0.0
        }
    )


@pytest.fixture
def sample_market_config():
    """Create sample market configuration."""
    return {
        'initial_demand': 1000.0,
        'initial_price_index': 1.0,
        'competition_intensity': 0.5,
        'base_price': 100.0,
        'num_competitors': 3,
        'price_elasticity': -1.5
    }


@pytest.fixture
def sample_market(sample_market_config):
    """Create a sample market for testing."""
    return Market(sample_market_config)


@pytest.fixture
def demand_calculator():
    """Create a demand calculator for testing."""
    return DemandCalculator(base_demand=1000.0, price_elasticity=-1.5)


@pytest.fixture
def pricing_engine():
    """Create a pricing engine for testing."""
    return PricingEngine(base_price=100.0)


@pytest.fixture
def competitor_ai():
    """Create competitor AI for testing."""
    return CompetitorAI(num_competitors=3)


@pytest.fixture
def trend_analyzer():
    """Create a trend analyzer for testing."""
    return TrendAnalyzer()


@pytest.fixture
def boom_market():
    """Create a booming market scenario."""
    config = {
        'initial_demand': 1500.0,
        'initial_price_index': 1.2,
        'competition_intensity': 0.7,
        'base_price': 120.0,
        'num_competitors': 4,
        'price_elasticity': -1.3
    }
    return Market(config)


@pytest.fixture
def recession_market():
    """Create a recession market scenario."""
    config = {
        'initial_demand': 600.0,
        'initial_price_index': 0.8,
        'competition_intensity': 0.9,
        'base_price': 80.0,
        'num_competitors': 5,
        'price_elasticity': -2.0
    }
    return Market(config)


@pytest.fixture
def stable_market():
    """Create a stable market scenario."""
    config = {
        'initial_demand': 1000.0,
        'initial_price_index': 1.0,
        'competition_intensity': 0.5,
        'base_price': 100.0,
        'num_competitors': 3,
        'price_elasticity': -1.5
    }
    return Market(config)


@pytest.fixture
def volatile_market():
    """Create a volatile market scenario."""
    config = {
        'initial_demand': 1200.0,
        'initial_price_index': 1.1,
        'competition_intensity': 0.8,
        'base_price': 110.0,
        'num_competitors': 4,
        'price_elasticity': -1.8
    }
    return Market(config)


@pytest.fixture
def market_conditions_boom():
    """Market conditions for boom economy."""
    return {
        'demand_level': 1500.0,
        'price_index': 1.2,
        'market_price': 120.0,
        'economic_indicators': {
            'gdp_growth': 0.05,
            'inflation': 0.02,
            'interest_rate': 0.03
        },
        'competition_intensity': 0.7
    }


@pytest.fixture
def market_conditions_recession():
    """Market conditions for recession."""
    return {
        'demand_level': 600.0,
        'price_index': 0.8,
        'market_price': 80.0,
        'economic_indicators': {
            'gdp_growth': -0.03,
            'inflation': 0.08,
            'interest_rate': 0.08
        },
        'competition_intensity': 0.9
    }


@pytest.fixture
def competitor_prices():
    """Sample competitor prices."""
    return [95.0, 105.0, 98.0]


@pytest.fixture
def company_factors_high_quality():
    """Company factors for high quality scenario."""
    return {
        'quality': 0.9,
        'brand_value': 80.0,
        'customer_satisfaction': 0.85
    }


@pytest.fixture
def company_factors_low_quality():
    """Company factors for low quality scenario."""
    return {
        'quality': 0.4,
        'brand_value': 20.0,
        'customer_satisfaction': 0.5
    }