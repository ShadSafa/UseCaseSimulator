"""
Unit tests for the Company module.
Tests company creation, financial calculations, decision making, and state updates.
"""

import pytest
from modules.core.company import (
    Company, FinancialData, OperationsData, ResourceData, MarketData,
    FinancialManager, OperationsManager, DecisionManager, ResourceManager
)


class TestFinancialData:
    """Test FinancialData dataclass."""

    def test_financial_data_creation(self):
        """Test creating FinancialData with default values."""
        data = FinancialData()
        assert data.revenue == 0.0
        assert data.costs == 0.0
        assert data.profit == 0.0
        assert data.cash == 0.0

    def test_financial_data_custom_values(self):
        """Test creating FinancialData with custom values."""
        data = FinancialData(revenue=100000, costs=80000, profit=20000, cash=50000)
        assert data.revenue == 100000
        assert data.costs == 80000
        assert data.profit == 20000
        assert data.cash == 50000


class TestOperationsData:
    """Test OperationsData dataclass."""

    def test_operations_data_creation(self):
        """Test creating OperationsData with default values."""
        data = OperationsData()
        assert data.capacity == 1000.0
        assert data.efficiency == 0.8
        assert data.quality == 0.75
        assert data.customer_satisfaction == 0.7

    def test_operations_data_custom_values(self):
        """Test creating OperationsData with custom values."""
        data = OperationsData(capacity=2000, efficiency=0.9, quality=0.85)
        assert data.capacity == 2000
        assert data.efficiency == 0.9
        assert data.quality == 0.85


class TestResourceData:
    """Test ResourceData dataclass."""

    def test_resource_data_creation(self):
        """Test creating ResourceData with default values."""
        data = ResourceData()
        assert data.employees == 100
        assert data.equipment == 100000.0
        assert data.inventory == 50000.0


class TestMarketData:
    """Test MarketData dataclass."""

    def test_market_data_creation(self):
        """Test creating MarketData with default values."""
        data = MarketData()
        assert data.market_share == 0.15
        assert data.brand_value == 50.0
        assert data.competitive_position == 0.5


class TestFinancialManager:
    """Test FinancialManager class."""

    def test_calculate_revenue(self):
        """Test revenue calculation."""
        financial_data = FinancialData()
        manager = FinancialManager(financial_data)

        revenue = manager.calculate_revenue(1000.0, 100.0, 0.15)
        expected = 100.0 * (1000.0 * 0.15)  # price * (demand * market_share)
        assert revenue == expected

    def test_calculate_costs(self):
        """Test cost calculation."""
        financial_data = FinancialData()
        operations_data = OperationsData(capacity=1000, utilization=0.8)
        resource_data = ResourceData(employees=100, equipment=100000, inventory=50000)

        manager = FinancialManager(financial_data)
        costs = manager.calculate_costs(operations_data, resource_data)

        # Should include operational, employee, equipment, and inventory costs
        assert costs > 0
        assert isinstance(costs, float)

    def test_calculate_profit(self):
        """Test profit calculation."""
        financial_data = FinancialData(revenue=100000, costs=80000)
        manager = FinancialManager(financial_data)

        profit = manager.calculate_profit()
        assert profit == 20000

    def test_update_financials(self):
        """Test updating financial data."""
        financial_data = FinancialData()
        manager = FinancialManager(financial_data)

        manager.update_financials(100000, 80000)

        assert financial_data.revenue == 100000
        assert financial_data.costs == 80000
        assert financial_data.profit == 20000
        assert financial_data.cash_flow > 0  # Profit minus depreciation
        assert financial_data.cash == financial_data.cash_flow


class TestOperationsManager:
    """Test OperationsManager class."""

    def test_update_efficiency(self):
        """Test efficiency updates."""
        operations_data = OperationsData(efficiency=0.8)
        manager = OperationsManager(operations_data)

        manager.update_efficiency(50000)  # Investment
        assert operations_data.efficiency > 0.8
        assert operations_data.efficiency <= 1.0

    def test_update_capacity(self):
        """Test capacity updates."""
        operations_data = OperationsData(capacity=1000)
        manager = OperationsManager(operations_data)

        manager.update_capacity(500)
        assert operations_data.capacity == 1500

    def test_calculate_utilization(self):
        """Test utilization calculation."""
        operations_data = OperationsData(capacity=1000)
        manager = OperationsManager(operations_data)

        utilization = manager.calculate_utilization(1200, 0.8)  # demand=1200, market_share=0.8
        expected_demand = 1200 * 0.8  # 960
        expected_utilization = min(1.0, 960 / 1000)  # 0.96

        assert utilization == expected_utilization
        assert operations_data.utilization == expected_utilization

    def test_update_quality(self):
        """Test quality updates."""
        operations_data = OperationsData(quality=0.75)
        manager = OperationsManager(operations_data)

        manager.update_quality(25000)  # Investment
        assert operations_data.quality > 0.75
        assert operations_data.quality <= 1.0

    def test_update_customer_satisfaction(self):
        """Test customer satisfaction updates."""
        operations_data = OperationsData(quality=0.8, customer_satisfaction=0.7)
        manager = OperationsManager(operations_data)

        manager.update_customer_satisfaction(0.8, 95.0, 100.0)  # quality, price, market_price
        assert operations_data.customer_satisfaction >= 0.7
        assert operations_data.customer_satisfaction <= 1.0


class TestDecisionManager:
    """Test DecisionManager class."""

    def test_make_decision_valid(self):
        """Test making valid decisions."""
        manager = DecisionManager()

        params = {'new_price': 110.0, 'round': 1}
        result = manager.make_decision('price_change', params)

        assert result is True
        assert len(manager.decision_history) == 1
        assert manager.decision_history[0]['type'] == 'price_change'

    def test_make_decision_invalid(self):
        """Test making invalid decisions."""
        manager = DecisionManager()

        # Invalid decision type
        result = manager.make_decision('invalid_decision', {})
        assert result is False
        assert len(manager.decision_history) == 0

        # Missing required parameters
        result = manager.make_decision('price_change', {})
        assert result is False
        assert len(manager.decision_history) == 0

    def test_get_recent_decisions(self):
        """Test getting recent decisions."""
        manager = DecisionManager()

        # Add multiple decisions
        for i in range(10):
            manager.make_decision('price_change', {'new_price': 100 + i, 'round': i})

        recent = manager.get_recent_decisions(5)
        assert len(recent) == 5
        assert recent[0]['params']['round'] == 4  # Most recent first (0-indexed rounds)


class TestResourceManager:
    """Test ResourceManager class."""

    def test_hire_employees(self):
        """Test hiring employees."""
        resource_data = ResourceData(employees=100)
        manager = ResourceManager(resource_data)

        manager.hire_employees(25)
        assert resource_data.employees == 125

    def test_purchase_equipment(self):
        """Test purchasing equipment."""
        resource_data = ResourceData(equipment=100000)
        manager = ResourceManager(resource_data)

        manager.purchase_equipment(50000)
        assert resource_data.equipment == 150000

    def test_update_inventory(self):
        """Test inventory updates."""
        resource_data = ResourceData(inventory=50000)
        manager = ResourceManager(resource_data)

        manager.update_inventory(10000)  # Add to inventory
        assert resource_data.inventory == 60000

        manager.update_inventory(-5000)  # Reduce inventory
        assert resource_data.inventory == 55000

    def test_get_resource_utilization(self):
        """Test resource utilization metrics."""
        resource_data = ResourceData(employees=100, equipment=100000, inventory=50000)
        manager = ResourceManager(resource_data)

        utilization = manager.get_resource_utilization()

        assert 'employee_productivity' in utilization
        assert 'equipment_utilization' in utilization
        assert 'inventory_turnover' in utilization

        assert utilization['employee_productivity'] == 100 / 100.0  # Normalized


class TestCompany:
    """Test Company class."""

    def test_company_creation(self, sample_company):
        """Test creating a company."""
        assert sample_company.id == 'test_company'
        assert sample_company.name == 'Test Company'
        assert sample_company.financial_data.revenue == 100000
        assert sample_company.operations_data.capacity == 1000
        assert sample_company.resource_data.employees == 100
        assert sample_company.market_data.market_share == 0.15

    def test_calculate_revenue(self, sample_company):
        """Test revenue calculation."""
        revenue = sample_company.calculate_revenue(1000.0, 100.0)
        expected = 100.0 * (1000.0 * 0.15)  # price * (demand * market_share)
        assert revenue == expected

    def test_calculate_costs(self, sample_company):
        """Test cost calculation."""
        costs = sample_company.calculate_costs()
        assert costs > 0
        assert isinstance(costs, float)

    def test_make_decision_price_change(self, sample_company):
        """Test making price change decisions."""
        params = {'new_price': 110.0, 'round': 1}
        result = sample_company.make_decision('price_change', params)

        assert result is True
        assert len(sample_company.decision_manager.decision_history) == 1

    def test_make_decision_capacity_expansion(self, sample_company):
        """Test making capacity expansion decisions."""
        initial_capacity = sample_company.operations_data.capacity
        params = {'expansion_amount': 500, 'round': 1}

        result = sample_company.make_decision('capacity_expansion', params)

        assert result is True
        assert sample_company.operations_data.capacity == initial_capacity + 500

    def test_make_decision_marketing_campaign(self, sample_company):
        """Test making marketing campaign decisions."""
        initial_brand_value = sample_company.market_data.brand_value
        initial_market_share = sample_company.market_data.market_share

        params = {'budget': 50000, 'round': 1}
        result = sample_company.make_decision('marketing_campaign', params)

        assert result is True
        assert sample_company.market_data.brand_value > initial_brand_value
        assert sample_company.market_data.market_share >= initial_market_share

    def test_make_decision_quality_improvement(self, sample_company):
        """Test making quality improvement decisions."""
        initial_quality = sample_company.operations_data.quality

        params = {'investment': 25000, 'round': 1}
        result = sample_company.make_decision('quality_improvement', params)

        assert result is True
        assert sample_company.operations_data.quality > initial_quality

    def test_make_decision_hiring(self, sample_company):
        """Test making hiring decisions."""
        initial_employees = sample_company.resource_data.employees

        params = {'num_employees': 25, 'round': 1}
        result = sample_company.make_decision('hiring', params)

        assert result is True
        assert sample_company.resource_data.employees == initial_employees + 25

    def test_make_decision_equipment_purchase(self, sample_company):
        """Test making equipment purchase decisions."""
        initial_equipment = sample_company.resource_data.equipment

        params = {'equipment_value': 75000, 'round': 1}
        result = sample_company.make_decision('equipment_purchase', params)

        assert result is True
        assert sample_company.resource_data.equipment == initial_equipment + 75000

    def test_update_state(self, sample_company):
        """Test updating company state."""
        market_conditions = {
            'demand_level': 1200.0,
            'price_index': 1.0,
            'price': 100.0,
            'market_price': 100.0,
            'economic_indicators': {'gdp_growth': 0.02, 'inflation': 0.03}
        }

        initial_satisfaction = sample_company.operations_data.customer_satisfaction

        sample_company.update_state(market_conditions)

        # Check that utilization was calculated
        assert sample_company.operations_data.utilization >= 0

        # Check that customer satisfaction was updated
        assert sample_company.operations_data.customer_satisfaction >= initial_satisfaction

        # Check that performance history was recorded
        assert len(sample_company.performance_history) > 0

    def test_get_kpis(self, sample_company):
        """Test getting KPIs."""
        kpis = sample_company.get_kpis()

        required_kpis = [
            'revenue', 'profit_margin', 'market_share', 'roi',
            'customer_satisfaction', 'operational_efficiency',
            'capacity_utilization', 'brand_value'
        ]

        for kpi in required_kpis:
            assert kpi in kpis
            assert isinstance(kpis[kpi], (int, float))

    def test_get_performance_trend(self, sample_company):
        """Test getting performance trends."""
        # Add some performance history
        for i in range(5):
            sample_company._record_performance()

        trend = sample_company.get_performance_trend('revenue', 3)
        assert len(trend) == 3
        assert all(isinstance(value, float) for value in trend)

    def test_to_dict_and_from_dict(self, sample_company):
        """Test serialization and deserialization."""
        # Convert to dict
        data = sample_company.to_dict()

        assert data['id'] == 'test_company'
        assert data['name'] == 'Test Company'
        assert 'financial_data' in data
        assert 'operations_data' in data
        assert 'resource_data' in data
        assert 'market_data' in data

        # Create new company from dict
        new_company = Company.from_dict(data)

        assert new_company.id == sample_company.id
        assert new_company.name == sample_company.name
        assert new_company.financial_data.revenue == sample_company.financial_data.revenue
        assert new_company.operations_data.capacity == sample_company.operations_data.capacity