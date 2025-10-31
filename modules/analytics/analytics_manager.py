from typing import Dict, List, Any, Optional
from datetime import datetime
from .kpi_calculator import KPICalculator, KPIMetrics
from .ranking_system import RankingSystem, RankingResult, RankingWeights
from .report_generator import ReportGenerator
from .leaderboard import Leaderboard
from .chart_generator import ChartGenerator


class AnalyticsManager:
    """Main orchestrator for analytics operations in the simulation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', 'data/analytics')

        # Initialize components
        self.kpi_calculator = KPICalculator()
        self.ranking_system = RankingSystem()
        self.report_generator = ReportGenerator(output_dir=f"{self.output_dir}/reports")
        self.leaderboard = Leaderboard(persistence_file=f"{self.output_dir}/leaderboard.json")
        self.chart_generator = ChartGenerator(output_dir=f"{self.output_dir}/charts")

        # Analytics history
        self.analytics_history: List[Dict[str, Any]] = []

    def process_round_analytics(self, companies_data: List[Dict[str, Any]],
                               market_data: Dict[str, Any],
                               round_number: int) -> Dict[str, Any]:
        """Process analytics for a simulation round.

        Args:
            companies_data: List of company data dictionaries
            market_data: Market conditions data
            round_number: Current round number

        Returns:
            Dictionary containing all analytics results
        """
        analytics_results = {
            'round_number': round_number,
            'timestamp': datetime.now(),
            'kpi_analysis': {},
            'rankings': {},
            'leaderboard_updates': {},
            'generated_reports': [],
            'generated_charts': []
        }

        # Calculate KPIs for all companies
        company_kpis = {}
        for company in companies_data:
            competitor_data = [c for c in companies_data if c['id'] != company['id']]
            kpis = self.kpi_calculator.calculate_all_kpis(company, market_data, competitor_data)
            company_kpis[company['id']] = kpis

        analytics_results['kpi_analysis'] = company_kpis

        # Generate rankings
        rankings = {}
        for category in ['overall', 'financial', 'operational', 'market', 'customer']:
            ranking_results = self.ranking_system.rank_companies(companies_data, market_data)
            rankings[category] = [self._ranking_result_to_dict(r) for r in ranking_results]

        analytics_results['rankings'] = rankings

        # Update leaderboards
        leaderboard_updates = {}
        for category in ['overall', 'financial', 'operational', 'market', 'customer']:
            entries = self.leaderboard.update_leaderboard(companies_data, market_data, category)
            leaderboard_updates[category] = [self._leaderboard_entry_to_dict(e) for e in entries]

        analytics_results['leaderboard_updates'] = leaderboard_updates

        # Generate automatic reports if configured
        if self.config.get('auto_generate_reports', False):
            report_files = self._generate_automatic_reports(companies_data, market_data, round_number)
            analytics_results['generated_reports'] = report_files

        # Generate automatic charts if configured
        if self.config.get('auto_generate_charts', False):
            chart_files = self._generate_automatic_charts(companies_data, market_data, round_number)
            analytics_results['generated_charts'] = chart_files

        # Store in history
        self.analytics_history.append(analytics_results)

        return analytics_results

    def generate_comprehensive_report(self, simulation_data: Dict[str, Any],
                                    report_type: str = "comprehensive") -> str:
        """Generate a comprehensive analytics report.

        Args:
            simulation_data: Complete simulation data
            report_type: Type of report to generate

        Returns:
            Path to generated report file
        """
        return self.report_generator.generate_simulation_report(simulation_data, report_type)

    def generate_kpi_report(self, companies_data: List[Dict[str, Any]],
                           market_data: Dict[str, Any]) -> str:
        """Generate a KPI-focused report.

        Args:
            companies_data: List of company data
            market_data: Market conditions

        Returns:
            Path to generated KPI report
        """
        return self.report_generator.generate_kpi_report(companies_data, market_data)

    def generate_ranking_report(self, companies_data: List[Dict[str, Any]],
                               market_data: Dict[str, Any]) -> str:
        """Generate a ranking report.

        Args:
            companies_data: List of company data
            market_data: Market conditions

        Returns:
            Path to generated ranking report
        """
        return self.report_generator.generate_ranking_report(companies_data, market_data)

    def generate_performance_charts(self, company_data: Dict[str, Any],
                                   historical_data: List[Dict[str, Any]]) -> List[str]:
        """Generate performance charts for a company.

        Args:
            company_data: Company data
            historical_data: Historical simulation data

        Returns:
            List of generated chart file paths
        """
        company_name = company_data.get('name', company_data.get('company_name', 'Company'))

        charts = []

        # KPI trend charts
        key_kpis = ['profit_margin', 'market_share', 'customer_satisfaction', 'operational_efficiency']
        for kpi in key_kpis:
            chart_file = self.chart_generator.generate_kpi_trend_chart(historical_data, kpi, company_name)
            if chart_file:
                charts.append(chart_file)

        # Multi-KPI chart
        chart_file = self.chart_generator.generate_multi_kpi_chart(historical_data, key_kpis, company_name)
        if chart_file:
            charts.append(chart_file)

        # Performance radar chart
        current_kpis = company_data.get('kpis', {})
        if current_kpis:
            chart_file = self.chart_generator.generate_performance_radar_chart(current_kpis, company_name)
            if chart_file:
                charts.append(chart_file)

        return charts

    def get_leaderboard(self, category: str = "overall", limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard entries for a category.

        Args:
            category: Leaderboard category
            limit: Maximum number of entries

        Returns:
            List of leaderboard entries as dictionaries
        """
        entries = self.leaderboard.get_leaderboard(category, limit)
        return [self._leaderboard_entry_to_dict(entry) for entry in entries]

    def get_company_analytics(self, company_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific company.

        Args:
            company_id: Company ID

        Returns:
            Dictionary containing company analytics
        """
        analytics = {
            'company_id': company_id,
            'current_rankings': {},
            'historical_performance': {},
            'achievements': [],
            'peer_comparison': {}
        }

        # Current rankings across categories
        for category in ['overall', 'financial', 'operational', 'market', 'customer']:
            rank_entry = self.leaderboard.get_company_rank(company_id, category)
            if rank_entry:
                analytics['current_rankings'][category] = self._leaderboard_entry_to_dict(rank_entry)

        # Historical performance
        analytics['historical_performance'] = self.leaderboard.get_historical_performance(company_id)

        # Achievements
        analytics['achievements'] = [self._achievement_to_dict(a) for a in self.leaderboard.get_company_achievements(company_id)]

        # Peer comparison
        if 'overall' in analytics['current_rankings']:
            analytics['peer_comparison'] = self.ranking_system.get_peer_comparison(company_id)

        return analytics

    def get_market_analytics(self, market_data: Dict[str, Any],
                           companies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get market-level analytics.

        Args:
            market_data: Market conditions
            companies_data: List of company data

        Returns:
            Dictionary containing market analytics
        """
        analytics = {
            'market_overview': market_data,
            'competition_analysis': {},
            'market_share_distribution': [],
            'trends': {}
        }

        # Market share distribution
        for company in companies_data:
            market_share = company.get('market_share', 0)
            company_name = company.get('name', company.get('company_name', f'Company {company["id"]}'))
            analytics['market_share_distribution'].append({
                'company': company_name,
                'market_share': market_share
            })

        # Sort by market share
        analytics['market_share_distribution'].sort(key=lambda x: x['market_share'], reverse=True)

        # Competition analysis
        total_companies = len(companies_data)
        market_shares = [c.get('market_share', 0) for c in companies_data]

        if market_shares:
            analytics['competition_analysis'] = {
                'total_companies': total_companies,
                'average_market_share': sum(market_shares) / len(market_shares),
                'market_concentration': sum(ms**2 for ms in market_shares),  # Herfindahl-Hirschman Index
                'dominant_players': len([ms for ms in market_shares if ms > 0.2])  # Companies with >20% share
            }

        return analytics

    def export_analytics_data(self, format: str = "json") -> str:
        """Export all analytics data.

        Args:
            format: Export format ("json" or "csv")

        Returns:
            Path to exported file or data string
        """
        if format == "json":
            return self.report_generator.generate_csv_report(
                self.analytics_history,
                "analytics_export",
                columns=['round_number', 'timestamp']
            )
        else:
            # For JSON, create a comprehensive export
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'analytics_history': self.analytics_history,
                'leaderboard_stats': self.leaderboard.get_leaderboard_stats(),
                'kpi_summary': self.kpi_calculator.get_kpi_summary()
            }

            import json
            filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = f"{self.output_dir}/exports/{filename}"

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            return filepath

    def set_ranking_weights(self, weights: RankingWeights):
        """Update ranking system weights.

        Args:
            weights: New ranking weights
        """
        self.ranking_system.set_custom_weights(weights)

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of current analytics state.

        Returns:
            Dictionary containing analytics summary
        """
        return {
            'total_rounds_analyzed': len(self.analytics_history),
            'leaderboard_stats': self.leaderboard.get_leaderboard_stats(),
            'kpi_summary': self.kpi_calculator.get_kpi_summary(),
            'ranking_history_length': len(self.ranking_system.historical_rankings),
            'last_analysis_timestamp': self.analytics_history[-1]['timestamp'] if self.analytics_history else None
        }

    def _generate_automatic_reports(self, companies_data: List[Dict[str, Any]],
                                  market_data: Dict[str, Any], round_number: int) -> List[str]:
        """Generate automatic reports based on configuration."""
        reports = []

        # Generate KPI report every 5 rounds
        if round_number % 5 == 0:
            report_file = self.generate_kpi_report(companies_data, market_data)
            reports.append(report_file)

        # Generate ranking report every round
        report_file = self.generate_ranking_report(companies_data, market_data)
        reports.append(report_file)

        return reports

    def _generate_automatic_charts(self, companies_data: List[Dict[str, Any]],
                                 market_data: Dict[str, Any], round_number: int) -> List[str]:
        """Generate automatic charts based on configuration."""
        charts = []

        # Generate market share pie chart every 3 rounds
        if round_number % 3 == 0:
            chart_file = self.chart_generator.generate_market_share_pie_chart(companies_data)
            if chart_file:
                charts.append(chart_file)

        # Generate ranking bar chart every round
        chart_file = self.chart_generator.generate_ranking_bar_chart(
            [{'company_name': c.get('name', f'Company {c["id"]}'), 'score': c.get('overall_score', 0), 'rank': i+1}
             for i, c in enumerate(companies_data)]
        )
        if chart_file:
            charts.append(chart_file)

        return charts

    def _ranking_result_to_dict(self, result: RankingResult) -> Dict[str, Any]:
        """Convert RankingResult to dictionary."""
        return {
            'company_id': result.company_id,
            'company_name': result.company_name,
            'rank': result.rank,
            'score': result.score,
            'criteria_scores': result.criteria_scores,
            'percentile': result.percentile,
            'trend': result.trend
        }

    def _leaderboard_entry_to_dict(self, entry) -> Dict[str, Any]:
        """Convert LeaderboardEntry to dictionary."""
        return {
            'company_id': entry.company_id,
            'company_name': entry.company_name,
            'score': entry.score,
            'rank': entry.rank,
            'criteria': entry.criteria,
            'achieved_at': entry.achieved_at.isoformat(),
            'metadata': entry.metadata
        }

    def _achievement_to_dict(self, achievement) -> Dict[str, Any]:
        """Convert Achievement to dictionary."""
        return {
            'name': achievement.name,
            'description': achievement.description,
            'criteria': achievement.criteria,
            'icon': achievement.icon,
            'rarity': achievement.rarity
        }