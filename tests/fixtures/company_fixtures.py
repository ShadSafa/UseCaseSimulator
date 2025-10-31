import pytest
from modules.core.company import (
    Company, FinancialData, OperationsData, ResourceData, MarketData,
    FinancialManager, OperationsManager, DecisionManager, ResourceManager
)


@pytest.fixture
def sample_financial_data():
    """Create sample financial data for testing."""
    return FinancialData(
        revenue=100000.0,
        costs=80000.0,
        profit=20000.0,
        cash_flow=15000.0,
        assets=200000.0,
        liabilities=150000.0,
        cash=50000.0
    )


@pytest.fixture
def sample_operations_data():
    """Create sample operations data for testing."""
    return OperationsData(
        capacity=1000.0,
        efficiency=0.8,
        quality=0.75,
        customer_satisfaction=0.7,
        utilization=0.0
    )


@pytest.fixture
def sample_resource_data():
    """Create sample resource data for testing."""
    return ResourceData(
        employees=100,
        equipment=100000.0,
        inventory=50000.0
    )


@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return MarketData(
        market_share=0.15,
        brand_value=50.0,
        competitive_position=0.5
    )


@pytest.fixture
def sample_company(sample_financial_data, sample_operations_data,
                  sample_resource_data, sample_market_data):
    """Create a sample company for testing."""
    return Company(
        id="test_company",
        name="Test Company",
        financial_data=sample_financial_data,
        operations_data=sample_operations_data,
        resource_data=sample_resource_data,
        market_data=sample_market_data
    )


@pytest.fixture
def financial_manager(sample_financial_data):
    """Create a financial manager for testing."""
    return FinancialManager(sample_financial_data)


@pytest.fixture
def operations_manager(sample_operations_data):
    """Create an operations manager for testing."""
    return OperationsManager(sample_operations_data)


@pytest.fixture
def resource_manager(sample_resource_data):
    """Create a resource manager for testing."""
    return ResourceManager(sample_resource_data)


@pytest.fixture
def decision_manager():
    """Create a decision manager for testing."""
    return DecisionManager()


@pytest.fixture
def startup_company():
    """Create a startup company with minimal resources."""
    return Company(
        id="startup",
        name="Startup Inc",
        financial_data=FinancialData(
            revenue=10000.0,
            costs=15000.0,
            profit=-5000.0,
            cash=10000.0,
            assets=50000.0,
            liabilities=40000.0
        ),
        operations_data=OperationsData(
            capacity=100.0,
            efficiency=0.6,
            quality=0.5,
            customer_satisfaction=0.6
        ),
        resource_data=ResourceData(
            employees=10,
            equipment=10000.0,
            inventory=5000.0
        ),
        market_data=MarketData(
            market_share=0.01,
            brand_value=10.0,
            competitive_position=0.3
        )
    )


@pytest.fixture
def established_company():
    """Create an established company with solid performance."""
    return Company(
        id="established",
        name="Established Corp",
        financial_data=FinancialData(
            revenue=500000.0,
            costs=400000.0,
            profit=100000.0,
            cash=200000.0,
            assets=1000000.0,
            liabilities=800000.0
        ),
        operations_data=OperationsData(
            capacity=5000.0,
            efficiency=0.85,
            quality=0.8,
            customer_satisfaction=0.8
        ),
        resource_data=ResourceData(
            employees=500,
            equipment=500000.0,
            inventory=100000.0
        ),
        market_data=MarketData(
            market_share=0.2,
            brand_value=100.0,
            competitive_position=0.7
        )
    )


@pytest.fixture
def struggling_company():
    """Create a struggling company facing difficulties."""
    return Company(
        id="struggling",
        name="Struggling LLC",
        financial_data=FinancialData(
            revenue=50000.0,
            costs=80000.0,
            profit=-30000.0,
            cash=5000.0,
            assets=100000.0,
            liabilities=95000.0
        ),
        operations_data=OperationsData(
            capacity=500.0,
            efficiency=0.5,
            quality=0.4,
            customer_satisfaction=0.4
        ),
        resource_data=ResourceData(
            employees=50,
            equipment=30000.0,
            inventory=20000.0
        ),
        market_data=MarketData(
            market_share=0.03,
            brand_value=15.0,
            competitive_position=0.2
        )
    )