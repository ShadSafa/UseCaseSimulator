from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from .kpi_calculator import KPICalculator


class RankingCriteria(Enum):
    """Enumeration of ranking criteria."""
    FINANCIAL_PERFORMANCE = "financial_performance"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    MARKET_POSITION = "market_position"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    OVERALL_SCORE = "overall_score"


@dataclass
class RankingResult:
    """Result of a ranking operation."""
    company_id: str
    company_name: str
    rank: int
    score: float
    criteria_scores: Dict[str, float]
    percentile: float
    trend: str  # "improving", "declining", "stable"


@dataclass
class RankingWeights:
    """Weights for different ranking criteria."""
    financial_weight: float = 0.3
    operational_weight: float = 0.25
    market_weight: float = 0.25
    customer_weight: float = 0.2

    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = sum([self.financial_weight, self.operational_weight,
                    self.market_weight, self.customer_weight])
        return abs(total - 1.0) < 0.001


class RankingSystem:
    """Multi-criteria ranking system for companies."""

    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = weights or RankingWeights()
        if not self.weights.validate():
            raise ValueError("Ranking weights must sum to 1.0")

        self.historical_rankings: List[List[RankingResult]] = []
        self.kpi_calculator = KPICalculator()

    def rank_companies(self, companies_data: List[Dict[str, Any]],
                      market_data: Dict[str, Any],
                      criteria: RankingCriteria = RankingCriteria.OVERALL_SCORE) -> List[RankingResult]:
        """Rank companies based on specified criteria.

        Args:
            companies_data: List of company data dictionaries
            market_data: Market conditions data
            criteria: Primary ranking criteria

        Returns:
            List of RankingResult objects, sorted by rank
        """
        if not companies_data:
            return []

        # Calculate KPIs for all companies
        company_kpis = []
        for company in companies_data:
            competitor_data = [c for c in companies_data if c['id'] != company['id']]
            kpis = self.kpi_calculator.calculate_all_kpis(company, market_data, competitor_data)
            company_kpis.append((company, kpis))

        # Calculate ranking scores
        ranking_results = []
        for company, kpis in company_kpis:
            score = self._calculate_ranking_score(kpis, criteria)
            criteria_scores = self._get_criteria_scores(kpis)
            trend = self._calculate_trend(company['id'])

            result = RankingResult(
                company_id=company['id'],
                company_name=company.get('name', company['id']),
                rank=0,  # Will be set after sorting
                score=score,
                criteria_scores=criteria_scores,
                percentile=0.0,  # Will be calculated
                trend=trend
            )
            ranking_results.append(result)

        # Sort by score (descending) and assign ranks
        ranking_results.sort(key=lambda x: x.score, reverse=True)

        total_companies = len(ranking_results)
        for i, result in enumerate(ranking_results):
            result.rank = i + 1
            result.percentile = (total_companies - i) / total_companies * 100

        # Store in history
        self.historical_rankings.append(ranking_results.copy())

        return ranking_results

    def _calculate_ranking_score(self, kpis: Any, criteria: RankingCriteria) -> float:
        """Calculate overall ranking score based on criteria."""
        if criteria == RankingCriteria.OVERALL_SCORE:
            return self._calculate_overall_score(kpis)
        elif criteria == RankingCriteria.FINANCIAL_PERFORMANCE:
            return self._calculate_financial_score(kpis.financial_kpis)
        elif criteria == RankingCriteria.OPERATIONAL_EFFICIENCY:
            return self._calculate_operational_score(kpis.operational_kpis)
        elif criteria == RankingCriteria.MARKET_POSITION:
            return self._calculate_market_score(kpis.market_kpis)
        elif criteria == RankingCriteria.CUSTOMER_SATISFACTION:
            return self._calculate_customer_score(kpis.customer_kpis)
        else:
            return self._calculate_overall_score(kpis)

    def _calculate_overall_score(self, kpis: Any) -> float:
        """Calculate weighted overall score."""
        financial_score = self._calculate_financial_score(kpis.financial_kpis)
        operational_score = self._calculate_operational_score(kpis.operational_kpis)
        market_score = self._calculate_market_score(kpis.market_kpis)
        customer_score = self._calculate_customer_score(kpis.customer_kpis)

        return (financial_score * self.weights.financial_weight +
                operational_score * self.weights.operational_weight +
                market_score * self.weights.market_weight +
                customer_score * self.weights.customer_weight)

    def _calculate_financial_score(self, financial_kpis: Dict[str, float]) -> float:
        """Calculate financial performance score (0-100)."""
        score = 0.0
        weights = {
            'profit_margin': 0.25,
            'return_on_assets': 0.25,
            'operating_cash_flow_ratio': 0.2,
            'current_ratio': 0.15,
            'revenue_growth_rate': 0.15
        }

        for kpi, weight in weights.items():
            value = financial_kpis.get(kpi, 0.0)
            # Normalize to 0-100 scale
            if kpi in ['profit_margin', 'return_on_assets', 'operating_cash_flow_ratio']:
                normalized = min(100.0, max(0.0, value * 100))
            elif kpi == 'current_ratio':
                normalized = min(100.0, max(0.0, value * 25))  # Target ratio around 4:1
            elif kpi == 'revenue_growth_rate':
                normalized = min(100.0, max(0.0, (value + 0.5) * 100))  # -50% to +50% growth
            else:
                normalized = min(100.0, max(0.0, value))

            score += normalized * weight

        return score

    def _calculate_operational_score(self, operational_kpis: Dict[str, float]) -> float:
        """Calculate operational efficiency score (0-100)."""
        score = 0.0
        weights = {
            'capacity_utilization': 0.3,
            'operational_efficiency': 0.25,
            'quality_index': 0.2,
            'employee_productivity': 0.15,
            'cost_per_unit_capacity': 0.1
        }

        for kpi, weight in weights.items():
            value = operational_kpis.get(kpi, 0.0)
            if kpi == 'cost_per_unit_capacity':
                # Lower cost is better, invert the scale
                normalized = max(0.0, 100.0 - min(100.0, value / 10))
            else:
                # Higher values are better
                normalized = min(100.0, max(0.0, value * 100))

            score += normalized * weight

        return score

    def _calculate_market_score(self, market_kpis: Dict[str, float]) -> float:
        """Calculate market position score (0-100)."""
        score = 0.0
        weights = {
            'market_share': 0.4,
            'competitive_position': 0.3,
            'brand_value_index': 0.2,
            'relative_market_position': 0.1
        }

        for kpi, weight in weights.items():
            value = market_kpis.get(kpi, 0.0)
            normalized = min(100.0, max(0.0, value * 100))
            score += normalized * weight

        return score

    def _calculate_customer_score(self, customer_kpis: Dict[str, float]) -> float:
        """Calculate customer satisfaction score (0-100)."""
        score = 0.0
        weights = {
            'customer_satisfaction_score': 0.4,
            'customer_loyalty_index': 0.3,
            'retention_probability': 0.2,
            'recommendation_likelihood': 0.1
        }

        for kpi, weight in weights.items():
            value = customer_kpis.get(kpi, 0.0)
            normalized = min(100.0, max(0.0, value * 100))
            score += normalized * weight

        return score

    def _get_criteria_scores(self, kpis: Any) -> Dict[str, float]:
        """Get individual criteria scores."""
        return {
            'financial': self._calculate_financial_score(kpis.financial_kpis),
            'operational': self._calculate_operational_score(kpis.operational_kpis),
            'market': self._calculate_market_score(kpis.market_kpis),
            'customer': self._calculate_customer_score(kpis.customer_kpis)
        }

    def _calculate_trend(self, company_id: str) -> str:
        """Calculate ranking trend for a company."""
        if len(self.historical_rankings) < 2:
            return "stable"

        current_rankings = self.historical_rankings[-1]
        previous_rankings = self.historical_rankings[-2]

        current_result = next((r for r in current_rankings if r.company_id == company_id), None)
        previous_result = next((r for r in previous_rankings if r.company_id == company_id), None)

        if not current_result or not previous_result:
            return "stable"

        rank_change = previous_result.rank - current_result.rank

        if rank_change > 1:
            return "improving"
        elif rank_change < -1:
            return "declining"
        else:
            return "stable"

    def get_peer_comparison(self, company_id: str, criteria: RankingCriteria = RankingCriteria.OVERALL_SCORE) -> Dict[str, Any]:
        """Get peer comparison data for a specific company."""
        if not self.historical_rankings:
            return {'status': 'no_ranking_data'}

        latest_rankings = self.historical_rankings[-1]
        company_result = next((r for r in latest_rankings if r.company_id == company_id), None)

        if not company_result:
            return {'status': 'company_not_found'}

        # Calculate peer statistics
        scores = [r.score for r in latest_rankings]
        avg_score = statistics.mean(scores)
        median_score = statistics.median(scores)

        return {
            'company_score': company_result.score,
            'company_rank': company_result.rank,
            'total_companies': len(latest_rankings),
            'percentile': company_result.percentile,
            'peer_average': avg_score,
            'peer_median': median_score,
            'above_average': company_result.score > avg_score,
            'trend': company_result.trend
        }

    def get_ranking_history(self, company_id: str, periods: int = 5) -> List[Dict[str, Any]]:
        """Get ranking history for a specific company."""
        history = []
        for i in range(min(periods, len(self.historical_rankings))):
            rankings = self.historical_rankings[-(i+1)]
            company_result = next((r for r in rankings if r.company_id == company_id), None)
            if company_result:
                history.append({
                    'period': -(i+1),
                    'rank': company_result.rank,
                    'score': company_result.score,
                    'percentile': company_result.percentile
                })

        return list(reversed(history))

    def get_top_performers(self, criteria: RankingCriteria = RankingCriteria.OVERALL_SCORE,
                          top_n: int = 5) -> List[RankingResult]:
        """Get top N performers based on criteria."""
        if not self.historical_rankings:
            return []

        latest_rankings = self.historical_rankings[-1]

        # Re-rank based on criteria if different from overall
        if criteria != RankingCriteria.OVERALL_SCORE:
            # This would require recalculating with different criteria
            # For now, return top N from current rankings
            pass

        return latest_rankings[:top_n]

    def set_custom_weights(self, weights: RankingWeights):
        """Update ranking weights."""
        if not weights.validate():
            raise ValueError("Custom weights must sum to 1.0")
        self.weights = weights