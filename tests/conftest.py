"""
Pytest configuration and shared fixtures for Use Case Simulator tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.core.company import Company, FinancialData, OperationsData, ResourceData, MarketData
from modules.core.market import Market, MarketState
from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.analytics.kpi_calculator import KPICalculator
from modules.analytics.ranking_system import RankingSystem


@pytest.fixture
def sample_company():
    """Create a sample company for testing."""
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
        id='test_company',
        name='Test Company',
        financial_data=financial_data,
        operations_data=operations_data,
        resource_data=resource_data,
        market_data=market_data
    )


@pytest.fixture
def sample_market():
    """Create a sample market for testing."""
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
def sample_simulation_engine():
    """Create a sample simulation engine for testing."""
    config = SimulationConfig(max_rounds=5, num_competitors=2)
    return SimulationEngine(config)


@pytest.fixture
def sample_kpi_calculator():
    """Create a sample KPI calculator for testing."""
    return KPICalculator()


@pytest.fixture
def sample_ranking_system():
    """Create a sample ranking system for testing."""
    return RankingSystem()


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create subdirectories
    (data_dir / "saves").mkdir()
    (data_dir / "scenarios").mkdir()
    (data_dir / "analytics").mkdir()
    (data_dir / "analytics" / "reports").mkdir()
    (data_dir / "analytics" / "charts").mkdir()
    (data_dir / "analytics" / "exports").mkdir()

    return data_dir


@pytest.fixture(autouse=True)
def mock_data_paths(monkeypatch, tmp_path):
    """Mock data paths to use temporary directories during testing."""
    # This would be used to redirect file operations to temp directories
    # Implementation depends on how the modules handle file paths
    pass