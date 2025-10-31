import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path
from .kpi_calculator import KPICalculator
from .ranking_system import RankingSystem


class ReportGenerator:
    """Generates various types of reports for simulation analytics."""

    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kpi_calculator = KPICalculator()
        self.ranking_system = RankingSystem()

    def generate_simulation_report(self, simulation_data: Dict[str, Any],
                                 report_type: str = "comprehensive") -> str:
        """Generate a comprehensive simulation report.

        Args:
            simulation_data: Complete simulation data
            report_type: Type of report ("comprehensive", "financial", "operational", "summary")

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_report_{report_type}_{timestamp}.json"

        if report_type == "comprehensive":
            report_data = self._generate_comprehensive_report(simulation_data)
        elif report_type == "financial":
            report_data = self._generate_financial_report(simulation_data)
        elif report_type == "operational":
            report_data = self._generate_operational_report(simulation_data)
        elif report_type == "summary":
            report_data = self._generate_summary_report(simulation_data)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def generate_csv_report(self, data: List[Dict[str, Any]],
                           filename: str, columns: Optional[List[str]] = None) -> str:
        """Generate a CSV report from data.

        Args:
            data: List of data dictionaries
            filename: Output filename (without extension)
            columns: Specific columns to include (None for all)

        Returns:
            Path to generated CSV file
        """
        if not data:
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"{filename}_{timestamp}.csv"

        if columns is None:
            columns = list(data[0].keys())

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for row in data:
                # Filter to specified columns and handle missing values
                filtered_row = {col: row.get(col, '') for col in columns}
                writer.writerow(filtered_row)

        return str(filepath)

    def generate_kpi_report(self, companies_data: List[Dict[str, Any]],
                           market_data: Dict[str, Any]) -> str:
        """Generate a KPI-focused report.

        Args:
            companies_data: List of company data
            market_data: Market conditions

        Returns:
            Path to generated KPI report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kpi_report_{timestamp}.json"

        kpi_data = []
        for company in companies_data:
            competitor_data = [c for c in companies_data if c['id'] != company['id']]
            kpis = self.kpi_calculator.calculate_all_kpis(company, market_data, competitor_data)

            company_kpi_data = {
                'company_id': company['id'],
                'company_name': company.get('name', company['id']),
                'financial_kpis': kpis.financial_kpis,
                'operational_kpis': kpis.operational_kpis,
                'market_kpis': kpis.market_kpis,
                'customer_kpis': kpis.customer_kpis,
                'calculated_at': kpis.calculated_at.isoformat()
            }
            kpi_data.append(company_kpi_data)

        # Add summary statistics
        summary = self._calculate_kpi_summary(kpi_data)
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_companies': len(kpi_data),
            'kpi_data': kpi_data,
            'summary_statistics': summary
        }

        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def generate_ranking_report(self, companies_data: List[Dict[str, Any]],
                               market_data: Dict[str, Any]) -> str:
        """Generate a ranking report.

        Args:
            companies_data: List of company data
            market_data: Market conditions

        Returns:
            Path to generated ranking report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ranking_report_{timestamp}.json"

        rankings = self.ranking_system.rank_companies(companies_data, market_data)

        ranking_data = []
        for result in rankings:
            ranking_data.append({
                'rank': result.rank,
                'company_id': result.company_id,
                'company_name': result.company_name,
                'overall_score': result.score,
                'criteria_scores': result.criteria_scores,
                'percentile': result.percentile,
                'trend': result.trend
            })

        report_data = {
            'generated_at': datetime.now().isoformat(),
            'ranking_criteria': 'overall_score',
            'total_companies': len(ranking_data),
            'rankings': ranking_data
        }

        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def generate_performance_trends_report(self, company_id: str,
                                         historical_data: List[Dict[str, Any]]) -> str:
        """Generate a performance trends report for a specific company.

        Args:
            company_id: ID of the company
            historical_data: Historical simulation data

        Returns:
            Path to generated trends report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trends_report_{company_id}_{timestamp}.json"

        trends_data = []
        for i, round_data in enumerate(historical_data):
            company_data = round_data.get('player_company', {})
            if company_data.get('id') == company_id:
                kpis = company_data.get('kpis', {})
                trends_data.append({
                    'round': i + 1,
                    'kpis': kpis,
                    'timestamp': round_data.get('timestamp', datetime.now().isoformat())
                })

        # Calculate trend analysis
        trend_analysis = self._analyze_trends(trends_data)

        report_data = {
            'generated_at': datetime.now().isoformat(),
            'company_id': company_id,
            'total_rounds': len(trends_data),
            'trends_data': trends_data,
            'trend_analysis': trend_analysis
        }

        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(filepath)

    def _generate_comprehensive_report(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive simulation report."""
        return {
            'report_type': 'comprehensive',
            'generated_at': datetime.now().isoformat(),
            'simulation_summary': simulation_data.get('simulation_summary', {}),
            'final_state': simulation_data.get('final_state', {}),
            'kpi_analysis': self._extract_kpi_analysis(simulation_data),
            'ranking_analysis': self._extract_ranking_analysis(simulation_data),
            'event_summary': simulation_data.get('event_summary', {}),
            'market_analysis': simulation_data.get('market_analysis', {})
        }

    def _generate_financial_report(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a financial-focused report."""
        return {
            'report_type': 'financial',
            'generated_at': datetime.now().isoformat(),
            'company_financials': simulation_data.get('company_financials', {}),
            'profitability_analysis': self._extract_profitability_analysis(simulation_data),
            'cash_flow_analysis': self._extract_cash_flow_analysis(simulation_data),
            'financial_ratios': self._extract_financial_ratios(simulation_data)
        }

    def _generate_operational_report(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an operational-focused report."""
        return {
            'report_type': 'operational',
            'generated_at': datetime.now().isoformat(),
            'operational_metrics': simulation_data.get('operational_metrics', {}),
            'efficiency_analysis': self._extract_efficiency_analysis(simulation_data),
            'capacity_analysis': self._extract_capacity_analysis(simulation_data),
            'quality_analysis': self._extract_quality_analysis(simulation_data)
        }

    def _generate_summary_report(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary report."""
        return {
            'report_type': 'summary',
            'generated_at': datetime.now().isoformat(),
            'simulation_overview': {
                'total_rounds': simulation_data.get('total_rounds', 0),
                'final_score': simulation_data.get('final_score', 0),
                'rank': simulation_data.get('final_rank', 0),
                'status': simulation_data.get('simulation_status', 'completed')
            },
            'key_metrics': simulation_data.get('key_metrics', {}),
            'achievements': simulation_data.get('achievements', []),
            'recommendations': simulation_data.get('recommendations', [])
        }

    def _calculate_kpi_summary(self, kpi_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for KPI data."""
        if not kpi_data:
            return {}

        summary = {
            'total_companies': len(kpi_data),
            'kpi_categories': ['financial', 'operational', 'market', 'customer'],
            'averages': {},
            'best_performers': {},
            'worst_performers': {}
        }

        # Calculate averages for each KPI category
        for category in summary['kpi_categories']:
            category_kpis = {}
            for company in kpi_data:
                for kpi_name, kpi_value in company[f'{category}_kpis'].items():
                    if kpi_name not in category_kpis:
                        category_kpis[kpi_name] = []
                    category_kpis[kpi_name].append(kpi_value)

            summary['averages'][category] = {
                kpi_name: sum(values) / len(values) for kpi_name, values in category_kpis.items()
            }

        return summary

    def _analyze_trends(self, trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends."""
        if len(trends_data) < 2:
            return {'status': 'insufficient_data'}

        analysis = {
            'improving_kpis': [],
            'declining_kpis': [],
            'stable_kpis': [],
            'trend_strength': {}
        }

        # Get all KPI names from first round
        if trends_data:
            all_kpis = set()
            for round_data in trends_data:
                all_kpis.update(round_data['kpis'].keys())

            for kpi_name in all_kpis:
                values = []
                for round_data in trends_data:
                    values.append(round_data['kpis'].get(kpi_name, 0))

                if len(values) >= 2:
                    # Simple trend analysis
                    trend = self._calculate_simple_trend(values)
                    analysis['trend_strength'][kpi_name] = trend

                    if trend > 0.1:
                        analysis['improving_kpis'].append(kpi_name)
                    elif trend < -0.1:
                        analysis['declining_kpis'].append(kpi_name)
                    else:
                        analysis['stable_kpis'].append(kpi_name)

        return analysis

    def _calculate_simple_trend(self, values: List[float]) -> float:
        """Calculate simple trend strength (-1 to 1)."""
        if len(values) < 2:
            return 0.0

        # Linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        if n * sum_x2 - sum_x ** 2 == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        # Normalize by average value to get relative trend
        avg_value = sum_y / n
        if avg_value == 0:
            return 0.0

        return slope / abs(avg_value)

    # Placeholder methods for data extraction (would be implemented based on actual data structure)
    def _extract_kpi_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_ranking_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_profitability_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_cash_flow_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_financial_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_efficiency_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_capacity_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}

    def _extract_quality_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'status': 'placeholder'}