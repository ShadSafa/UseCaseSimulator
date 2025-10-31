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
        data = FinancialData(
            revenue=100000.0,
            costs=80000.0,
            profit=20000.0,
            cash=50000.0
        )
        assert data.revenue == 100000.0
        assert data.costs == 80000.0
        assert data.profit == 20000.0
        assert data.cash == 50000.0


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
        data = OperationsData(
            capacity=2000.0,
            efficiency=0.9,
            quality=0.85,
            customer_satisfaction=0.8
        )
        assert data.capacity == 2000.0
        assert data.efficiency == 0.9
        assert data.quality == 0.85
        assert data.customer_satisfaction == 0.8


class TestResourceData:
    """Test ResourceData dataclass."""

    def test_resource_data_creation(self):
        """Test creating ResourceData with default values."""
        data = ResourceData()
        assert data.employees == 100
        assert data.equipment == 100000.0
        assert data.inventory == 50000.0

    def test_resource_data_custom_values(self):
        """Test creating ResourceData with custom values."""
        data = ResourceData(
            employees=200,
            equipment=200000.0,
            inventory=100000.0
        )
        assert data.employees == 200
        assert data.equipment == 200000.0
        assert data.inventory == 100000.0


class TestMarketData:
    """Test MarketData dataclass."""

    def test_market_data_creation(self):
        """Test creating MarketData with default values."""
        data = MarketData()
        assert data.market_share == 0.15
        assert data.brand_value == 50.0
        assert data.competitive_position == 0.5

    def test_market_data_custom_values(self):
        """Test creating MarketData with custom values."""
        data = MarketData(
            market_share=0.25,
            brand_value=75.0,
            competitive_position=0.7
        )
        assert data.market_share == 0.25
        assert data.brand_value == 75.0
        assert data.competitive_position == 0.7


class TestFinancialManager:
    """Test FinancialManager class."""

    def test_calculate_revenue(self, financial_manager):
        """Test revenue calculation."""
        revenue = financial_manager.calculate_revenue(
            market_demand=1000.0,
            price=100.0,
            market_share=0.15
        )
        expected = 100.0 * (1000.0 * 0.15)  # 15000.0
        assert revenue == expected

    def test_calculate_costs(self, financial_manager, sample_operations_data, sample_resource_data):
        """Test cost calculation."""
        costs = financial_manager.calculate_costs(sample_operations_data, sample_resource_data)

        # Should include operational costs, employee costs, equipment maintenance, and inventory holding
        assert costs > 0
        assert isinstance(costs, float)

    def test_calculate_profit(self, financial_manager):
        """Test profit calculation."""
        financial_manager.data.revenue = 100000.0
        financial_manager.data.costs = 80000.0

        profit = financial_manager.calculate_profit()
        assert profit == 20000.0

    def test_update_financials(self, financial_manager):
        """Test updating financial data."""
        financial_manager.update_financials(revenue=120000.0, costs=90000.0)

        assert financial_manager.data.revenue == 120000.0
        assert financial_manager.data.costs == 90000.0
        assert financial_manager.data.profit == 30000.0
        assert financial_manager.data.cash_flow == 30000.0 - (200000.0 * 0.1)  # Profit - depreciation


class TestOperationsManager:
    """Test OperationsManager class."""

    def test_update_efficiency(self, operations_manager):
        """Test efficiency update with investment."""
        initial_efficiency = operations_manager.data.efficiency
        operations_manager.update_efficiency(100000.0)

        assert operations_manager.data.efficiency > initial_efficiency
        assert operations_manager.data.efficiency <= 1.0

    def test_update_capacity(self, operations_manager):
        """Test capacity update."""
        initial_capacity = operations_manager.data.capacity
        operations_manager.update_capacity(500.0)

        assert operations_manager.data.capacity == initial_capacity + 500.0

    def test_calculate_utilization(self, operations_manager):
        """Test utilization calculation."""
        utilization = operations_manager.calculate_utilization(
            demand=800.0,
            market_share=0.15
        )

        expected = min(1.0, (800.0 * 0.15) / 1000.0)
        assert utilization == expected
        assert operations_manager.data.utilization == expected

    def test_update_quality(self, operations_manager):
        """Test quality update with investment."""
        initial_quality = operations_manager.data.quality
        operations_manager.update_quality(50000.0)

        assert operations_manager.data.quality > initial_quality
        assert operations_manager.data.quality <= 1.0

    def test_update_customer_satisfaction(self, operations_manager):
        """Test customer satisfaction update."""
        operations_manager.update_customer_satisfaction(
            quality=0.8,
            price=100.0,
            market_price=100.0
        )

        assert 0.0 <= operations_manager.data.customer_satisfaction <= 1.0


class TestDecisionManager:
    """Test DecisionManager class."""

    def test_make_decision_valid(self, decision_manager):
        """Test making a valid decision."""
        params = {'new_price': 105.0}
        success = decision_manager.make_decision('price_change', params)

        assert success is True
        assert len(decision_manager.decision_history) == 1
        assert decision_manager.decision_history[0]['type'] == 'price_change'

    def test_make_decision_invalid_type(self, decision_manager):
        """Test making an invalid decision type."""
        params = {'invalid_param': 'value'}
        success = decision_manager.make_decision('invalid_type', params)

        assert success is False
        assert len(decision_manager.decision_history) == 0

    def test_make_decision_missing_params(self, decision_manager):
        """Test making a decision with missing parameters."""
        params = {}  # Missing required 'new_price'
        success = decision_manager.make_decision('price_change', params)

        assert success is False
        assert len(decision_manager.decision_history) == 0

    def test_get_recent_decisions(self, decision_manager):
        """Test getting recent decisions."""
        # Add multiple decisions
        decisions = [
            {'type': 'price_change', 'params': {'new_price': 105.0}, 'round': 1},
            {'type': 'capacity_expansion', 'params': {'expansion_amount': 200.0}, 'round': 2},
            {'type': 'marketing_campaign', 'params': {'budget': 10000.0}, 'round': 3}
        ]

        for decision in decisions:
            decision_manager.decision_history.append(decision)

        recent = decision_manager.get_recent_decisions(2)
        assert len(recent) == 2
        assert recent[0]['round'] == 2
        assert recent[1]['round'] == 3


class TestResourceManager:
    """Test ResourceManager class."""

    def test_hire_employees(self, resource_manager):
        """Test hiring employees."""
        initial_employees = resource_manager.data.employees
        resource_manager.hire_employees(10)

        assert resource_manager.data.employees == initial_employees + 10

    def test_purchase_equipment(self, resource_manager):
        """Test purchasing equipment."""
        initial_equipment = resource_manager.data.equipment
        resource_manager.purchase_equipment(50000.0)

        assert resource_manager.data.equipment == initial_equipment + 50000.0

    def test_update_inventory(self, resource_manager):
        """Test updating inventory."""
        initial_inventory = resource_manager.data.inventory
        resource_manager.update_inventory(10000.0)

        assert resource_manager.data.inventory == initial_inventory + 10000.0

    def test_update_inventory_negative(self, resource_manager):
        """Test reducing inventory (cannot go below 0)."""
        resource_manager.update_inventory(-60000.0)

        assert resource_manager.data.inventory == 0.0

    def test_get_resource_utilization(self, resource_manager):
        """Test getting resource utilization metrics."""
        utilization = resource_manager.get_resource_utilization()

        assert 'employee_productivity' in utilization
        assert 'equipment_utilization' in utilization
        assert 'inventory_turnover' in utilization

        assert utilization['employee_productivity'] == 100 / 100.0  # employees / 100
        assert utilization['equipment_utilization'] == 0.8  # placeholder
        assert utilization['inventory_turnover'] == 4.0  # placeholder


class TestCompany:
    """Test Company class."""

    def test_company_creation(self, sample_company):
        """Test creating a company."""
        assert sample_company.id == "test_company"
        assert sample_company.name == "Test Company"
        assert sample_company.financial_data is not None
        assert sample_company.operations_data is not None
        assert sample_company.resource_data is not None
        assert sample_company.market_data is not None

    def test_calculate_revenue(self, sample_company):
        """Test company revenue calculation."""
        revenue = sample_company.calculate_revenue(
            market_demand=1000.0,
            price=100.0
        )

        expected = 100.0 * (1000.0 * 0.15)  # price * (demand * market_share)
        assert revenue == expected

    def test_calculate_costs(self, sample_company):
        """Test company cost calculation."""
        costs = sample_company.calculate_costs()
        assert costs > 0
        assert isinstance(costs, float)

    def test_make_decision_price_change(self, sample_company):
        """Test making a price change decision."""
        params = {'new_price': 105.0, 'round': 1}
        success = sample_company.make_decision('price_change', params)

        assert success is True
        assert len(sample_company.decision_manager.decision_history) == 1

    def test_make_decision_capacity_expansion(self, sample_company):
        """Test making a capacity expansion decision."""
        initial_capacity = sample_company.operations_data.capacity
        params = {'expansion_amount': 200.0, 'round': 1}
        success = sample_company.make_decision('capacity_expansion', params)

        assert success is True
        assert sample_company.operations_data.capacity == initial_capacity + 200.0

    def test_make_decision_marketing_campaign(self, sample_company):
        """Test making a marketing campaign decision."""
        initial_brand_value = sample_company.market_data.brand_value
        params = {'budget': 10000.0, 'round': 1}
        success = sample_company.make_decision('marketing_campaign', params)

        assert success is True
        assert sample_company.market_data.brand_value > initial_brand_value

    def test_make_decision_quality_improvement(self, sample_company):
        """Test making a quality improvement decision."""
        initial_quality = sample_company.operations_data.quality
        params = {'investment': 50000.0, 'round': 1}
        success = sample_company.make_decision('quality_improvement', params)

        assert success is True
        assert sample_company.operations_data.quality > initial_quality

    def test_make_decision_hiring(self, sample_company):
        """Test making a hiring decision."""
        initial_employees = sample_company.resource_data.employees
        params = {'num_employees': 10, 'round': 1}
        success = sample_company.make_decision('hiring', params)

        assert success is True
        assert sample_company.resource_data.employees == initial_employees + 10

    def test_make_decision_equipment_purchase(self, sample_company):
        """Test making an equipment purchase decision."""
        initial_equipment = sample_company.resource_data.equipment
        params = {'equipment_value': 25000.0, 'round': 1}
        success = sample_company.make_decision('equipment_purchase', params)

        assert success is True
        assert sample_company.resource_data.equipment == initial_equipment + 25000.0

    def test_update_state(self, sample_company, market_conditions_boom):
        """Test updating company state with market conditions."""
        sample_company.update_state(market_conditions_boom)

        # Check that utilization was calculated
        assert sample_company.operations_data.utilization >= 0.0

        # Check that customer satisfaction was updated
        assert 0.0 <= sample_company.operations_data.customer_satisfaction <= 1.0

        # Check that financials were updated
        assert sample_company.financial_data.revenue >= 0.0
        assert sample_company.financial_data.costs >= 0.0
        assert sample_company.financial_data.profit == sample_company.financial_data.revenue - sample_company.financial_data.costs

    def test_get_kpis(self, sample_company):
        """Test getting company KPIs."""
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
        sample_company.performance_history = [
            {'revenue': 90000.0, 'profit': 18000.0, 'market_share': 0.14},
            {'revenue': 95000.0, 'profit': 19000.0, 'market_share': 0.145},
            {'revenue': 100000.0, 'profit': 20000.0, 'market_share': 0.15}
        ]

        trend = sample_company.get_performance_trend('revenue', periods=3)
        assert len(trend) == 3
        assert trend == [90000.0, 95000.0, 100000.0]

    def test_to_dict(self, sample_company):
        """Test converting company to dictionary."""
        data = sample_company.to_dict()

        assert data['id'] == "test_company"
        assert data['name'] == "Test Company"
        assert 'financial_data' in data
        assert 'operations_data' in data
        assert 'resource_data' in data
        assert 'market_data' in data
        assert 'decision_history' in data
        assert 'performance_history' in data

    def test_from_dict(self, sample_company):
        """Test creating company from dictionary."""
        data = sample_company.to_dict()
        new_company = Company.from_dict(data)

        assert new_company.id == sample_company.id
        assert new_company.name == sample_company.name
        assert new_company.financial_data.revenue == sample_company.financial_data.revenue
        assert new_company.operations_data.capacity == sample_company.operations_data.capacity