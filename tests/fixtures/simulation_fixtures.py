import pytest
from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.core.simulation_state import SimulationState


@pytest.fixture
def simulation_config():
    """Create a standard simulation configuration for testing."""
    return SimulationConfig(
        max_rounds=10,
        num_competitors=3,
        initial_market_demand=1000.0,
        market_volatility=0.1,
        event_frequency=0.3
    )


@pytest.fixture
def simulation_engine(simulation_config):
    """Create a simulation engine for testing."""
    return SimulationEngine(simulation_config)


@pytest.fixture
def initialized_simulation_engine(simulation_engine):
    """Create and initialize a simulation engine."""
    simulation_engine.initialize_simulation()
    return simulation_engine


@pytest.fixture
def sample_simulation_state():
    """Create a sample simulation state for testing."""
    from modules.core.company import Company, FinancialData, OperationsData, ResourceData, MarketData
    from modules.core.market import Market

    # Create sample company
    company = Company(
        id="test_player",
        name="Test Player Company",
        financial_data=FinancialData(
            revenue=100000.0,
            costs=80000.0,
            profit=20000.0,
            cash=50000.0,
            assets=200000.0,
            liabilities=150000.0
        ),
        operations_data=OperationsData(
            capacity=1000.0,
            efficiency=0.8,
            quality=0.75,
            customer_satisfaction=0.7
        ),
        resource_data=ResourceData(
            employees=100,
            equipment=100000.0,
            inventory=50000.0
        ),
        market_data=MarketData(
            market_share=0.15,
            brand_value=50.0,
            competitive_position=0.5
        )
    )

    # Create sample market
    market_config = {
        'initial_demand': 1000.0,
        'initial_price_index': 1.0,
        'competition_intensity': 0.5,
        'base_price': 100.0,
        'num_competitors': 3
    }
    market = Market(market_config)

    # Create sample competitors
    competitors = [
        {
            'id': 'comp1',
            'name': 'Competitor 1',
            'market_share': 0.25,
            'aggressiveness': 0.6,
            'financials': {'revenue': 80000.0, 'profit': 15000.0}
        },
        {
            'id': 'comp2',
            'name': 'Competitor 2',
            'market_share': 0.2,
            'aggressiveness': 0.7,
            'financials': {'revenue': 70000.0, 'profit': 12000.0}
        },
        {
            'id': 'comp3',
            'name': 'Competitor 3',
            'market_share': 0.18,
            'aggressiveness': 0.5,
            'financials': {'revenue': 60000.0, 'profit': 10000.0}
        }
    ]

    # Create sample events
    events = []

    # Create sample KPIs
    kpis = {
        'profit_margin': 0.2,
        'market_share': 0.15,
        'customer_satisfaction': 0.7,
        'operational_efficiency': 0.8
    }

    return SimulationState(
        round_number=1,
        player_company=company,
        market=market,
        competitors=competitors,
        events=events,
        kpis=kpis
    )


@pytest.fixture
def player_decisions():
    """Create sample player decisions for testing."""
    return {
        'price_change': {'new_price': 105.0},
        'capacity_expansion': {'expansion_amount': 200.0},
        'marketing_campaign': {'budget': 10000.0},
        'quality_improvement': {'investment': 15000.0},
        'hiring': {'num_employees': 10}
    }


@pytest.fixture
def round_results():
    """Create sample round results for testing."""
    return {
        'revenue': 110000.0,
        'costs': 85000.0,
        'profit': 25000.0,
        'market_share': 0.16,
        'customer_satisfaction': 0.72,
        'efficiency': 0.82
    }


@pytest.fixture
def short_simulation_config():
    """Create a short simulation config for faster testing."""
    return SimulationConfig(
        max_rounds=3,
        num_competitors=2,
        initial_market_demand=500.0,
        market_volatility=0.05,
        event_frequency=0.1
    )


@pytest.fixture
def long_simulation_config():
    """Create a long simulation config for comprehensive testing."""
    return SimulationConfig(
        max_rounds=20,
        num_competitors=4,
        initial_market_demand=2000.0,
        market_volatility=0.2,
        event_frequency=0.4
    )


@pytest.fixture
def simulation_with_events(simulation_engine):
    """Create a simulation engine with some events for testing."""
    simulation_engine.initialize_simulation()

    # Add some test events
    from modules.core.event_manager import Event
    test_events = [
        Event(
            id="test_event_1",
            name="Market Boom",
            description="Market demand increases significantly",
            type="market_event",
            impacts={"demand_change": 0.2},
            duration=2,
            probability=0.3
        ),
        Event(
            id="test_event_2",
            name="Cost Increase",
            description="Operational costs rise due to external factors",
            type="company_event",
            impacts={"cost_change": 0.15},
            duration=1,
            probability=0.2
        )
    ]

    for event in test_events:
        simulation_engine.event_manager.active_events.append({
            'event': event.to_dict(),
            'remaining_rounds': event.duration,
            'start_round': 1
        })

    return simulation_engine