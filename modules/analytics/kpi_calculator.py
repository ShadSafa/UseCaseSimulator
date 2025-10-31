from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics
from datetime import datetime, timedelta


@dataclass
class KPIMetrics:
    """Container for KPI calculation results."""
    financial_kpis: Dict[str, float]
    operational_kpis: Dict[str, float]
    market_kpis: Dict[str, float]
    customer_kpis: Dict[str, float]
    calculated_at: datetime


class KPICalculator:
    """Advanced KPI calculator for business simulation analytics."""

    def __init__(self):
        self.kpi_history: List[KPIMetrics] = []
        self.baseline_periods = 3  # Number of periods for baseline calculations

    def calculate_all_kpis(self, company_data: Dict[str, Any],
                          market_data: Dict[str, Any],
                          competitor_data: List[Dict[str, Any]]) -> KPIMetrics:
        """Calculate all KPI categories for a company.

        Args:
            company_data: Dictionary containing company financial, operational, and market data
            market_data: Dictionary containing market conditions and trends
            competitor_data: List of competitor company data

        Returns:
            KPIMetrics object with all calculated KPIs
        """
        financial_kpis = self._calculate_financial_kpis(company_data)
        operational_kpis = self._calculate_operational_kpis(company_data)
        market_kpis = self._calculate_market_kpis(company_data, market_data, competitor_data)
        customer_kpis = self._calculate_customer_kpis(company_data)

        metrics = KPIMetrics(
            financial_kpis=financial_kpis,
            operational_kpis=operational_kpis,
            market_kpis=market_kpis,
            customer_kpis=customer_kpis,
            calculated_at=datetime.now()
        )

        self.kpi_history.append(metrics)
        return metrics

    def _calculate_financial_kpis(self, company_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial performance KPIs."""
        financial = company_data.get('financial_data', {})

        revenue = financial.get('revenue', 0.0)
        costs = financial.get('costs', 0.0)
        profit = financial.get('profit', 0.0)
        assets = financial.get('assets', 0.0)
        liabilities = financial.get('liabilities', 0.0)
        cash = financial.get('cash', 0.0)
        cash_flow = financial.get('cash_flow', 0.0)

        kpis = {}

        # Profitability ratios
        kpis['profit_margin'] = profit / revenue if revenue > 0 else 0.0
        kpis['gross_margin'] = (revenue - costs) / revenue if revenue > 0 else 0.0
        kpis['return_on_assets'] = profit / assets if assets > 0 else 0.0
        kpis['return_on_equity'] = profit / (assets - liabilities) if (assets - liabilities) > 0 else 0.0

        # Liquidity ratios
        kpis['current_ratio'] = cash / liabilities if liabilities > 0 else 0.0
        kpis['cash_ratio'] = cash / liabilities if liabilities > 0 else 0.0

        # Cash flow metrics
        kpis['operating_cash_flow_ratio'] = cash_flow / revenue if revenue > 0 else 0.0
        kpis['cash_flow_margin'] = cash_flow / revenue if revenue > 0 else 0.0

        # Growth rates (if historical data available)
        kpis.update(self._calculate_financial_growth_rates())

        return kpis

    def _calculate_operational_kpis(self, company_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate operational efficiency KPIs."""
        operations = company_data.get('operations_data', {})
        resources = company_data.get('resource_data', {})

        capacity = operations.get('capacity', 0.0)
        utilization = operations.get('utilization', 0.0)
        efficiency = operations.get('efficiency', 0.0)
        quality = operations.get('quality', 0.0)

        employees = resources.get('employees', 0)
        equipment_value = resources.get('equipment', 0.0)
        inventory_value = resources.get('inventory', 0.0)

        kpis = {}

        # Capacity and utilization
        kpis['capacity_utilization'] = utilization
        kpis['operational_efficiency'] = efficiency
        kpis['production_efficiency'] = utilization * efficiency

        # Quality metrics
        kpis['quality_index'] = quality
        kpis['defect_rate'] = max(0.0, 1.0 - quality)  # Inverse of quality

        # Resource productivity
        kpis['employee_productivity'] = capacity / employees if employees > 0 else 0.0
        kpis['asset_turnover'] = capacity / equipment_value if equipment_value > 0 else 0.0
        kpis['inventory_turnover'] = capacity / inventory_value if inventory_value > 0 else 0.0

        # Cost efficiency
        financial = company_data.get('financial_data', {})
        total_costs = financial.get('costs', 0.0)
        kpis['cost_per_unit_capacity'] = total_costs / capacity if capacity > 0 else 0.0

        return kpis

    def _calculate_market_kpis(self, company_data: Dict[str, Any],
                              market_data: Dict[str, Any],
                              competitor_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate market position and competitive KPIs."""
        market = company_data.get('market_data', {})

        market_share = market.get('market_share', 0.0)
        brand_value = market.get('brand_value', 0.0)
        competitive_position = market.get('competitive_position', 0.0)

        kpis = {}

        # Market position
        kpis['market_share'] = market_share
        kpis['brand_value_index'] = brand_value
        kpis['competitive_position'] = competitive_position

        # Market concentration (if competitor data available)
        if competitor_data:
            total_market_share = market_share + sum(comp.get('market_share', 0.0) for comp in competitor_data)
            kpis['market_concentration'] = market_share / total_market_share if total_market_share > 0 else 0.0

            # Relative market position
            competitor_shares = [comp.get('market_share', 0.0) for comp in competitor_data]
            if competitor_shares:
                avg_competitor_share = statistics.mean(competitor_shares)
                kpis['relative_market_position'] = market_share / avg_competitor_share if avg_competitor_share > 0 else 0.0

        # Market dynamics
        market_demand = market_data.get('demand_level', 1000.0)
        kpis['demand_capture_rate'] = market_share * market_demand / 1000.0  # Normalized

        return kpis

    def _calculate_customer_kpis(self, company_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate customer-related KPIs."""
        operations = company_data.get('operations_data', {})

        satisfaction = operations.get('customer_satisfaction', 0.0)
        quality = operations.get('quality', 0.0)

        kpis = {}

        # Satisfaction metrics
        kpis['customer_satisfaction_score'] = satisfaction
        kpis['customer_loyalty_index'] = satisfaction * quality  # Combined metric

        # Quality perception
        kpis['perceived_quality'] = quality
        kpis['satisfaction_gap'] = satisfaction - quality  # Gap between satisfaction and quality

        # Derived metrics
        kpis['retention_probability'] = min(1.0, satisfaction * 0.8 + quality * 0.2)
        kpis['recommendation_likelihood'] = satisfaction * quality

        return kpis

    def _calculate_financial_growth_rates(self) -> Dict[str, float]:
        """Calculate growth rates from historical KPI data."""
        if len(self.kpi_history) < 2:
            return {
                'revenue_growth_rate': 0.0,
                'profit_growth_rate': 0.0,
                'margin_growth_rate': 0.0
            }

        current = self.kpi_history[-1]
        previous = self.kpi_history[-2]

        growth_rates = {}

        # Revenue growth
        current_rev = current.financial_kpis.get('profit_margin', 0.0) * 1000000  # Estimate from margin
        prev_rev = previous.financial_kpis.get('profit_margin', 0.0) * 1000000
        growth_rates['revenue_growth_rate'] = (current_rev - prev_rev) / prev_rev if prev_rev > 0 else 0.0

        # Profit growth
        current_profit = current.financial_kpis.get('return_on_assets', 0.0) * 1000000
        prev_profit = previous.financial_kpis.get('return_on_assets', 0.0) * 1000000
        growth_rates['profit_growth_rate'] = (current_profit - prev_profit) / prev_profit if prev_profit > 0 else 0.0

        # Margin growth
        current_margin = current.financial_kpis.get('profit_margin', 0.0)
        prev_margin = previous.financial_kpis.get('profit_margin', 0.0)
        growth_rates['margin_growth_rate'] = current_margin - prev_margin

        return growth_rates

    def get_kpi_trends(self, kpi_name: str, periods: int = 5) -> List[float]:
        """Get trend data for a specific KPI over recent periods."""
        if len(self.kpi_history) < periods:
            return []

        trends = []
        for i in range(min(periods, len(self.kpi_history))):
            metrics = self.kpi_history[-(i+1)]

            # Extract KPI value from appropriate category
            value = 0.0
            for category in ['financial_kpis', 'operational_kpis', 'market_kpis', 'customer_kpis']:
                category_data = getattr(metrics, category)
                if kpi_name in category_data:
                    value = category_data[kpi_name]
                    break

            trends.append(value)

        return list(reversed(trends))  # Most recent last

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Get a summary of current KPI status."""
        if not self.kpi_history:
            return {'status': 'no_kpi_data'}

        latest = self.kpi_history[-1]

        return {
            'total_kpis_calculated': len(latest.financial_kpis) + len(latest.operational_kpis) +
                                   len(latest.market_kpis) + len(latest.customer_kpis),
            'financial_kpi_count': len(latest.financial_kpis),
            'operational_kpi_count': len(latest.operational_kpis),
            'market_kpi_count': len(latest.market_kpis),
            'customer_kpi_count': len(latest.customer_kpis),
            'last_calculated': latest.calculated_at.isoformat(),
            'history_length': len(self.kpi_history)
        }

    def calculate_custom_kpi(self, name: str, formula: str, data: Dict[str, Any]) -> float:
        """Calculate a custom KPI using a simple formula.

        Args:
            name: Name of the custom KPI
            formula: Simple formula string (e.g., 'revenue / costs')
            data: Data dictionary containing variables for the formula

        Returns:
            Calculated KPI value
        """
        try:
            # Simple evaluation with safety checks
            allowed_names = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            return eval(formula, {"__builtins__": {}}, allowed_names)
        except:
            return 0.0