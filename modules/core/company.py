from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import copy


@dataclass
class FinancialData:
    """Financial attributes of the company."""
    revenue: float = 0.0
    costs: float = 0.0
    profit: float = 0.0
    cash_flow: float = 0.0
    assets: float = 0.0
    liabilities: float = 0.0
    cash: float = 0.0


@dataclass
class OperationsData:
    """Operational attributes of the company."""
    capacity: float = 1000.0
    efficiency: float = 0.8
    quality: float = 0.75
    customer_satisfaction: float = 0.7
    utilization: float = 0.0


@dataclass
class ResourceData:
    """Resource attributes of the company."""
    employees: int = 100
    equipment: float = 100000.0  # Value of equipment
    inventory: float = 50000.0   # Value of inventory


@dataclass
class MarketData:
    """Market position attributes of the company."""
    market_share: float = 0.15
    brand_value: float = 50.0
    competitive_position: float = 0.5  # 0-1 scale


class FinancialManager:
    """Manages financial calculations and operations."""

    def __init__(self, financial_data: FinancialData):
        self.data = financial_data

    def calculate_revenue(self, market_demand: float, price: float, market_share: float) -> float:
        """Calculate revenue based on market conditions."""
        # Simplified: revenue = price * (demand * market_share)
        return price * (market_demand * market_share)

    def calculate_costs(self, operations_data: OperationsData, resource_data: ResourceData) -> float:
        """Calculate total costs including operational and resource costs."""
        # Operational costs based on capacity utilization
        operational_costs = operations_data.capacity * operations_data.utilization * 50.0  # Base cost per unit

        # Resource costs
        employee_costs = resource_data.employees * 50000.0  # Annual salary per employee
        equipment_maintenance = resource_data.equipment * 0.05  # 5% maintenance cost
        inventory_holding = resource_data.inventory * 0.02  # 2% holding cost

        total_costs = operational_costs + employee_costs + equipment_maintenance + inventory_holding
        return total_costs

    def calculate_profit(self) -> float:
        """Calculate profit as revenue minus costs."""
        return self.data.revenue - self.data.costs

    def update_financials(self, revenue: float, costs: float):
        """Update financial data."""
        self.data.revenue = revenue
        self.data.costs = costs
        self.data.profit = self.calculate_profit()
        # Simplified cash flow and balance sheet updates
        self.data.cash_flow = self.data.profit - (self.data.assets * 0.1)  # Depreciation etc.
        self.data.cash += self.data.cash_flow


class OperationsManager:
    """Manages operational aspects of the company."""

    def __init__(self, operations_data: OperationsData):
        self.data = operations_data

    def update_efficiency(self, investment: float):
        """Update operational efficiency based on investments."""
        # Efficiency improves with investment, but with diminishing returns
        improvement = min(investment / 100000.0, 0.1)
        self.data.efficiency = min(1.0, self.data.efficiency + improvement)

    def update_capacity(self, expansion: float):
        """Update production capacity."""
        self.data.capacity += expansion

    def calculate_utilization(self, demand: float, market_share: float) -> float:
        """Calculate capacity utilization."""
        required_capacity = demand * market_share
        utilization = min(1.0, required_capacity / self.data.capacity) if self.data.capacity > 0 else 0.0
        self.data.utilization = utilization
        return utilization

    def update_quality(self, quality_investment: float):
        """Update product quality."""
        improvement = min(quality_investment / 50000.0, 0.1)
        self.data.quality = min(1.0, self.data.quality + improvement)

    def update_customer_satisfaction(self, quality: float, price: float, market_price: float):
        """Update customer satisfaction based on quality and price competitiveness."""
        quality_factor = quality
        price_factor = 1.0 - abs(price - market_price) / market_price
        self.data.customer_satisfaction = min(1.0, (quality_factor + price_factor) / 2.0)


class DecisionManager:
    """Handles business decisions and their impacts."""

    def __init__(self):
        self.decision_history: List[Dict[str, Any]] = []

    def make_decision(self, decision_type: str, params: Dict[str, Any]) -> bool:
        """Process a business decision."""
        # Validate decision
        if not self._validate_decision(decision_type, params):
            return False

        # Record decision
        decision_record = {
            'type': decision_type,
            'params': params,
            'timestamp': datetime.now(),
            'round': params.get('round', 0)
        }
        self.decision_history.append(decision_record)

        # Decision is processed successfully
        return True

    def _validate_decision(self, decision_type: str, params: Dict[str, Any]) -> bool:
        """Validate decision parameters."""
        # Basic validation - can be expanded
        required_params = {
            'price_change': ['new_price'],
            'capacity_expansion': ['expansion_amount'],
            'marketing_campaign': ['budget'],
            'quality_improvement': ['investment'],
            'hiring': ['num_employees'],
            'equipment_purchase': ['equipment_value']
        }

        if decision_type not in required_params:
            return False

        for param in required_params[decision_type]:
            if param not in params:
                return False

        return True

    def get_recent_decisions(self, rounds: int = 5) -> List[Dict[str, Any]]:
        """Get recent decisions."""
        return self.decision_history[-rounds:] if self.decision_history else []


class ResourceManager:
    """Manages company resources."""

    def __init__(self, resource_data: ResourceData):
        self.data = resource_data

    def hire_employees(self, num_employees: int):
        """Hire new employees."""
        self.data.employees += num_employees

    def purchase_equipment(self, equipment_value: float):
        """Purchase new equipment."""
        self.data.equipment += equipment_value

    def update_inventory(self, change: float):
        """Update inventory levels."""
        self.data.inventory = max(0.0, self.data.inventory + change)

    def get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization metrics."""
        return {
            'employee_productivity': self.data.employees / 100.0,  # Normalized
            'equipment_utilization': 0.8,  # Placeholder
            'inventory_turnover': 4.0  # Placeholder
        }


@dataclass
class Company:
    """Main Company class representing a business entity in the simulation."""

    id: str
    name: str
    financial_data: FinancialData = field(default_factory=FinancialData)
    operations_data: OperationsData = field(default_factory=OperationsData)
    resource_data: ResourceData = field(default_factory=ResourceData)
    market_data: MarketData = field(default_factory=MarketData)

    # Managers
    financial_manager: FinancialManager = None
    operations_manager: OperationsManager = None
    decision_manager: DecisionManager = field(default_factory=DecisionManager)
    resource_manager: ResourceManager = None

    # Performance tracking
    performance_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        # Initialize managers if not provided
        if self.financial_manager is None:
            self.financial_manager = FinancialManager(self.financial_data)
        if self.operations_manager is None:
            self.operations_manager = OperationsManager(self.operations_data)
        if self.resource_manager is None:
            self.resource_manager = ResourceManager(self.resource_data)

    def calculate_revenue(self, market_demand: float, price: float) -> float:
        """Calculate company revenue."""
        return self.financial_manager.calculate_revenue(market_demand, price, self.market_data.market_share)

    def calculate_costs(self) -> float:
        """Calculate company costs."""
        return self.financial_manager.calculate_costs(self.operations_data, self.resource_data)

    def make_decision(self, decision_type: str, params: Dict[str, Any]) -> bool:
        """Make a business decision."""
        success = self.decision_manager.make_decision(decision_type, params)
        if success:
            self._apply_decision_impact(decision_type, params)
        return success

    def _apply_decision_impact(self, decision_type: str, params: Dict[str, Any]):
        """Apply the impact of a decision to company state."""
        if decision_type == 'price_change':
            # Price changes affect market share (simplified)
            pass  # Would need market context
        elif decision_type == 'capacity_expansion':
            self.operations_manager.update_capacity(params['expansion_amount'])
        elif decision_type == 'marketing_campaign':
            # Marketing affects brand value and market share
            budget = params['budget']
            self.market_data.brand_value += budget / 10000.0
            self.market_data.market_share = min(0.5, self.market_data.market_share + budget / 1000000.0)
        elif decision_type == 'quality_improvement':
            self.operations_manager.update_quality(params['investment'])
        elif decision_type == 'hiring':
            self.resource_manager.hire_employees(params['num_employees'])
        elif decision_type == 'equipment_purchase':
            self.resource_manager.purchase_equipment(params['equipment_value'])

    def update_state(self, market_conditions: Dict[str, Any]):
        """Update company state based on market conditions."""
        # Update operations based on market
        demand = market_conditions.get('demand_level', 1000.0)
        price = market_conditions.get('price_index', 1.0) * 100.0  # Assume base price
        market_price = market_conditions.get('market_price', 100.0)

        # Calculate utilization
        self.operations_manager.calculate_utilization(demand, self.market_data.market_share)

        # Update customer satisfaction
        self.operations_manager.update_customer_satisfaction(
            self.operations_data.quality, price, market_price
        )

        # Update financials
        revenue = self.calculate_revenue(demand, price)
        costs = self.calculate_costs()
        self.financial_manager.update_financials(revenue, costs)

        # Record performance
        self._record_performance()

    def _record_performance(self):
        """Record current performance metrics."""
        current_metrics = {
            'timestamp': datetime.now(),
            'revenue': self.financial_data.revenue,
            'profit': self.financial_data.profit,
            'market_share': self.market_data.market_share,
            'customer_satisfaction': self.operations_data.customer_satisfaction,
            'efficiency': self.operations_data.efficiency
        }
        self.performance_history.append(current_metrics)

        # Keep only last 50 records to prevent memory issues
        if len(self.performance_history) > 50:
            self.performance_history.pop(0)

    def get_kpis(self) -> Dict[str, float]:
        """Get current Key Performance Indicators."""
        return {
            'revenue': self.financial_data.revenue,
            'profit_margin': self.financial_data.profit / self.financial_data.revenue if self.financial_data.revenue > 0 else 0,
            'market_share': self.market_data.market_share,
            'roi': self.financial_data.profit / self.financial_data.assets if self.financial_data.assets > 0 else 0,
            'customer_satisfaction': self.operations_data.customer_satisfaction,
            'operational_efficiency': self.operations_data.efficiency,
            'capacity_utilization': self.operations_data.utilization,
            'brand_value': self.market_data.brand_value
        }

    def get_performance_trend(self, metric: str, periods: int = 5) -> List[float]:
        """Get performance trend for a specific metric."""
        if len(self.performance_history) < periods:
            return [getattr(self, f'get_{metric}')() for _ in range(len(self.performance_history))]

        return [record.get(metric, 0.0) for record in self.performance_history[-periods:]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert company to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'financial_data': {
                'revenue': self.financial_data.revenue,
                'costs': self.financial_data.costs,
                'profit': self.financial_data.profit,
                'cash_flow': self.financial_data.cash_flow,
                'assets': self.financial_data.assets,
                'liabilities': self.financial_data.liabilities,
                'cash': self.financial_data.cash
            },
            'operations_data': {
                'capacity': self.operations_data.capacity,
                'efficiency': self.operations_data.efficiency,
                'quality': self.operations_data.quality,
                'customer_satisfaction': self.operations_data.customer_satisfaction,
                'utilization': self.operations_data.utilization
            },
            'resource_data': {
                'employees': self.resource_data.employees,
                'equipment': self.resource_data.equipment,
                'inventory': self.resource_data.inventory
            },
            'market_data': {
                'market_share': self.market_data.market_share,
                'brand_value': self.market_data.brand_value,
                'competitive_position': self.market_data.competitive_position
            },
            'decision_history': self.decision_manager.decision_history,
            'performance_history': self.performance_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Company':
        """Create company from dictionary."""
        financial_data = FinancialData(**data.get('financial_data', {}))
        operations_data = OperationsData(**data.get('operations_data', {}))
        resource_data = ResourceData(**data.get('resource_data', {}))
        market_data = MarketData(**data.get('market_data', {}))

        company = cls(
            id=data['id'],
            name=data['name'],
            financial_data=financial_data,
            operations_data=operations_data,
            resource_data=resource_data,
            market_data=market_data
        )

        # Restore decision history
        company.decision_manager.decision_history = data.get('decision_history', [])

        # Restore performance history
        company.performance_history = data.get('performance_history', [])

        return company