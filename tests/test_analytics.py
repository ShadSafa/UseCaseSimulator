"""
Unit tests for the Analytics module.
Tests KPI calculations, ranking systems, report generation, leaderboards, and chart generation.
"""

import pytest
import os
from modules.analytics.kpi_calculator import KPICalculator, KPIMetrics
from modules.analytics.ranking_system import RankingSystem, RankingCriteria, RankingWeights
from modules.analytics.report_generator import ReportGenerator
from modules.analytics.leaderboard import Leaderboard, LeaderboardEntry, Achievement
from modules.analytics.analytics_manager import AnalyticsManager


class TestKPICalculator:
    """Test KPICalculator class."""

    def test_kpi_calculator_creation(self):
        """Test creating KPI calculator."""
        calculator = KPICalculator()
        assert len(calculator.kpi_history) == 0
        assert calculator.baseline_periods == 3

    def test_calculate_all_kpis(self, sample_kpi_calculator, sample_company, sample_market):
        """Test calculating all KPIs."""
        competitor_data = [
            {'market_share': 0.20, 'name': 'Competitor A'},
            {'market_share': 0.18, 'name': 'Competitor B'}
        ]

        metrics = sample_kpi_calculator.calculate_all_kpis(
            sample_company.to_dict(),
            {'demand_level': 1000.0, 'price_index': 1.0},
            competitor_data
        )

        assert isinstance(metrics, KPIMetrics)
        assert len(metrics.financial_kpis) > 0
        assert len(metrics.operational_kpis) > 0
        assert len(metrics.market_kpis) > 0
        assert len(metrics.customer_kpis) > 0
        assert metrics.calculated_at is not None

        # Check that history was recorded
        assert len(sample_kpi_calculator.kpi_history) == 1

    def test_calculate_financial_kpis(self, sample_kpi_calculator):
        """Test financial KPI calculations."""
        company_data = {
            'financial_data': {
                'revenue': 100000,
                'costs': 75000,
                'profit': 25000,
                'assets': 200000,
                'liabilities': 150000,
                'cash': 50000,
                'cash_flow': 30000
            }
        }

        kpis = sample_kpi_calculator._calculate_financial_kpis(company_data)

        assert 'profit_margin' in kpis
        assert 'return_on_assets' in kpis
        assert 'current_ratio' in kpis
        assert kpis['profit_margin'] == 0.25  # 25000/100000
        assert kpis['return_on_assets'] == 0.125  # 25000/200000

    def test_calculate_operational_kpis(self, sample_kpi_calculator):
        """Test operational KPI calculations."""
        company_data = {
            'operations_data': {
                'capacity': 1000,
                'utilization': 0.8,
                'efficiency': 0.85,
                'quality': 0.9
            },
            'resource_data': {
                'employees': 100,
                'equipment': 100000,
                'inventory': 50000
            },
            'financial_data': {
                'costs': 80000
            }
        }

        kpis = sample_kpi_calculator._calculate_operational_kpis(company_data)

        assert 'capacity_utilization' in kpis
        assert 'operational_efficiency' in kpis
        assert 'employee_productivity' in kpis
        assert kpis['capacity_utilization'] == 0.8
        assert kpis['operational_efficiency'] == 0.85

    def test_calculate_market_kpis(self, sample_kpi_calculator):
        """Test market KPI calculations."""
        company_data = {
            'market_data': {
                'market_share': 0.15,
                'brand_value': 50.0,
                'competitive_position': 0.6
            }
        }
        market_data = {'demand_level': 1000.0}
        competitor_data = [
            {'market_share': 0.20},
            {'market_share': 0.18}
        ]

        kpis = sample_kpi_calculator._calculate_market_kpis(company_data, market_data, competitor_data)

        assert 'market_share' in kpis
        assert 'competitive_position' in kpis
        assert 'relative_market_position' in kpis
        assert kpis['market_share'] == 0.15

    def test_calculate_customer_kpis(self, sample_kpi_calculator):
        """Test customer KPI calculations."""
        company_data = {
            'operations_data': {
                'customer_satisfaction': 0.85,
                'quality': 0.9
            }
        }

        kpis = sample_kpi_calculator._calculate_customer_kpis(company_data)

        assert 'customer_satisfaction_score' in kpis
        assert 'retention_probability' in kpis
        assert 'recommendation_likelihood' in kpis
        assert kpis['customer_satisfaction_score'] == 0.85

    def test_get_kpi_trends(self, sample_kpi_calculator, sample_company, sample_market):
        """Test getting KPI trends."""
        competitor_data = [{'market_share': 0.20}]

        # Add multiple KPI calculations
        for i in range(5):
            # Modify company data slightly for each calculation
            company_dict = sample_company.to_dict()
            company_dict['financial_data']['revenue'] = 100000 + (i * 5000)

            sample_kpi_calculator.calculate_all_kpis(
                company_dict,
                {'demand_level': 1000.0, 'price_index': 1.0},
                competitor_data
            )

        trends = sample_kpi_calculator.get_kpi_trends('profit_margin', 3)
        assert len(trends) == 3
        assert all(isinstance(value, float) for value in trends)

    def test_get_kpi_summary(self, sample_kpi_calculator):
        """Test getting KPI summary."""
        # No history
        summary = sample_kpi_calculator.get_kpi_summary()
        assert summary['status'] == 'no_kpi_data'

        # Add some history
        sample_kpi_calculator.kpi_history = [
            KPIMetrics(
                financial_kpis={'profit_margin': 0.2, 'roi': 0.15},
                operational_kpis={'efficiency': 0.8, 'utilization': 0.75},
                market_kpis={'market_share': 0.15, 'brand_value': 50.0},
                customer_kpis={'satisfaction': 0.85, 'loyalty': 0.8},
                calculated_at=None
            )
        ]

        summary = sample_kpi_calculator.get_kpi_summary()
        assert 'total_kpis_calculated' in summary
        assert 'financial_kpi_count' in summary
        assert summary['financial_kpi_count'] == 2
        assert summary['operational_kpi_count'] == 2

    def test_calculate_custom_kpi(self, sample_kpi_calculator):
        """Test calculating custom KPIs."""
        data = {'revenue': 100000, 'costs': 80000, 'profit': 20000}

        # Test valid formula
        result = sample_kpi_calculator.calculate_custom_kpi('margin', 'profit / revenue', data)
        assert result == 0.2

        # Test invalid formula
        result = sample_kpi_calculator.calculate_custom_kpi('invalid', 'invalid_formula', data)
        assert result == 0.0


class TestRankingSystem:
    """Test RankingSystem class."""

    def test_ranking_system_creation(self):
        """Test creating ranking system."""
        system = RankingSystem()
        assert len(system.historical_rankings) == 0
        assert system.weights.financial_weight == 0.3
        assert system.weights.operational_weight == 0.25

    def test_ranking_system_custom_weights(self):
        """Test ranking system with custom weights."""
        weights = RankingWeights(financial_weight=0.4, operational_weight=0.3, market_weight=0.2, customer_weight=0.1)
        system = RankingSystem(weights)

        assert system.weights.financial_weight == 0.4
        assert system.weights.operational_weight == 0.3

    def test_invalid_weights(self):
        """Test invalid weights validation."""
        weights = RankingWeights(financial_weight=0.5, operational_weight=0.3, market_weight=0.2, customer_weight=0.1)
        # Should not sum to 1.0
        with pytest.raises(ValueError, match="Ranking weights must sum to 1.0"):
            RankingSystem(weights)

    def test_rank_companies(self, sample_ranking_system, sample_company, sample_market):
        """Test ranking companies."""
        companies_data = [
            sample_company.to_dict(),
            {
                'id': 'comp2',
                'name': 'Competitor 2',
                'financial_data': {'revenue': 120000, 'costs': 90000, 'profit': 30000, 'assets': 250000, 'liabilities': 180000, 'cash': 70000},
                'operations_data': {'capacity': 1200, 'efficiency': 0.9, 'quality': 0.85, 'customer_satisfaction': 0.8, 'utilization': 0.0},
                'resource_data': {'employees': 120, 'equipment': 120000, 'inventory': 60000},
                'market_data': {'market_share': 0.18, 'brand_value': 60.0, 'competitive_position': 0.7}
            }
        ]

        rankings = sample_ranking_system.rank_companies(companies_data, {'demand_level': 1000.0})

        assert len(rankings) == 2
        assert rankings[0].rank == 1
        assert rankings[1].rank == 2
        assert all(isinstance(r, list) for r in sample_ranking_system.historical_rankings)

    def test_get_peer_comparison(self, sample_ranking_system, sample_company, sample_market):
        """Test getting peer comparison."""
        # No rankings yet
        comparison = sample_ranking_system.get_peer_comparison('test_company')
        assert comparison['status'] == 'no_ranking_data'

        # Add some rankings
        companies_data = [sample_company.to_dict()]
        sample_ranking_system.rank_companies(companies_data, {'demand_level': 1000.0})

        comparison = sample_ranking_system.get_peer_comparison('test_company')
        assert 'company_score' in comparison
        assert 'company_rank' in comparison
        assert 'percentile' in comparison

    def test_get_ranking_history(self, sample_ranking_system, sample_company, sample_market):
        """Test getting ranking history."""
        companies_data = [sample_company.to_dict()]

        # Add multiple rankings
        for i in range(3):
            sample_ranking_system.rank_companies(companies_data, {'demand_level': 1000.0})

        history = sample_ranking_system.get_ranking_history('test_company', 2)
        assert len(history) == 2
        assert all('rank' in h and 'score' in h for h in history)

    def test_set_custom_weights(self, sample_ranking_system):
        """Test setting custom weights."""
        new_weights = RankingWeights(financial_weight=0.5, operational_weight=0.2, market_weight=0.2, customer_weight=0.1)
        sample_ranking_system.set_custom_weights(new_weights)

        assert sample_ranking_system.weights.financial_weight == 0.5


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_report_generator_creation(self, tmp_path):
        """Test creating report generator."""
        output_dir = tmp_path / "reports"
        generator = ReportGenerator(str(output_dir))

        assert generator.output_dir.exists()

    def test_generate_csv_report(self, tmp_path):
        """Test generating CSV report."""
        generator = ReportGenerator(str(tmp_path / "reports"))

        data = [
            {'name': 'Company A', 'revenue': 100000, 'profit': 20000},
            {'name': 'Company B', 'revenue': 120000, 'profit': 25000}
        ]

        filepath = generator.generate_csv_report(data, "test_report")
        assert filepath.endswith('.csv')

        # Check file contents
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'name,revenue,profit' in content
            assert 'Company A,100000,20000' in content

    def test_generate_kpi_report(self, tmp_path, sample_company, sample_market):
        """Test generating KPI report."""
        generator = ReportGenerator(str(tmp_path / "reports"))

        companies_data = [sample_company.to_dict()]
        competitor_data = [{'market_share': 0.20}]

        filepath = generator.generate_kpi_report(companies_data, {'demand_level': 1000.0})
        assert filepath.endswith('.json')

        # Check file exists and has content
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            import json
            data = json.load(f)
            assert 'kpi_data' in data
            assert 'summary_statistics' in data

    def test_generate_ranking_report(self, tmp_path, sample_company, sample_market):
        """Test generating ranking report."""
        generator = ReportGenerator(str(tmp_path / "reports"))

        companies_data = [sample_company.to_dict()]

        filepath = generator.generate_ranking_report(companies_data, {'demand_level': 1000.0})
        assert filepath.endswith('.json')

        # Check file exists
        assert os.path.exists(filepath)


class TestLeaderboard:
    """Test Leaderboard class."""

    def test_leaderboard_creation(self, tmp_path):
        """Test creating leaderboard."""
        persistence_file = str(tmp_path / "leaderboard.json")
        leaderboard = Leaderboard(persistence_file)

        assert len(leaderboard.leaderboards) > 0
        assert 'overall' in leaderboard.leaderboards
        assert 'financial' in leaderboard.leaderboards

    def test_update_leaderboard(self, sample_company, sample_market):
        """Test updating leaderboard."""
        leaderboard = Leaderboard()

        companies_data = [sample_company.to_dict()]
        entries = leaderboard.update_leaderboard(companies_data, {'demand_level': 1000.0}, 'overall')

        assert len(entries) == 1
        assert entries[0].company_id == 'test_company'
        assert entries[0].rank == 1

    def test_get_leaderboard(self):
        """Test getting leaderboard."""
        leaderboard = Leaderboard()

        # Empty leaderboard initially
        entries = leaderboard.get_leaderboard('overall')
        # Note: Leaderboard may have entries from previous tests, so just check it's a list
        assert isinstance(entries, list)

        # Add some entries
        leaderboard.leaderboards['overall'] = [
            LeaderboardEntry('comp1', 'Company 1', 85.0, 1, 'overall', None, {}),
            LeaderboardEntry('comp2', 'Company 2', 75.0, 2, 'overall', None, {})
        ]

        entries = leaderboard.get_leaderboard('overall', 1)
        assert len(entries) == 1
        assert entries[0].company_id == 'comp1'

    def test_get_company_rank(self):
        """Test getting company rank."""
        leaderboard = Leaderboard()

        # Company not found
        entry = leaderboard.get_company_rank('nonexistent')
        assert entry is None

        # Add company
        leaderboard.leaderboards['overall'] = [
            LeaderboardEntry('test_company', 'Test Company', 80.0, 1, 'overall', None, {})
        ]

        entry = leaderboard.get_company_rank('test_company')
        assert entry is not None
        assert entry.score == 80.0
        assert entry.rank == 1

    def test_export_leaderboard(self):
        """Test exporting leaderboard."""
        leaderboard = Leaderboard()

        # Add some data
        leaderboard.leaderboards['overall'] = [
            LeaderboardEntry('comp1', 'Company 1', 90.0, 1, 'overall', None, {}),
            LeaderboardEntry('comp2', 'Company 2', 80.0, 2, 'overall', None, {})
        ]

        # Export as JSON
        json_data = leaderboard.export_leaderboard('overall', 'json')
        assert 'entries' in json_data
        assert len(json_data['entries']) == 2

        # Export as CSV
        csv_data = leaderboard.export_leaderboard('overall', 'csv')
        assert 'Rank,Company Name,Score' in csv_data
        assert 'Company 1,90.0' in csv_data


class TestAnalyticsManager:
    """Test AnalyticsManager class."""

    def test_analytics_manager_creation(self, tmp_path):
        """Test creating analytics manager."""
        config = {'output_dir': str(tmp_path / "analytics")}
        manager = AnalyticsManager(config)

        assert manager.kpi_calculator is not None
        assert manager.ranking_system is not None
        assert manager.report_generator is not None
        assert manager.leaderboard is not None

    def test_process_round_analytics(self, sample_company, sample_market):
        """Test processing round analytics."""
        manager = AnalyticsManager()

        companies_data = [sample_company.to_dict()]
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        results = manager.process_round_analytics(companies_data, market_data, 1)

        assert 'round_number' in results
        assert 'kpi_analysis' in results
        assert 'rankings' in results
        assert 'leaderboard_updates' in results
        assert results['round_number'] == 1

    def test_get_company_analytics(self):
        """Test getting company analytics."""
        manager = AnalyticsManager()

        # No data
        analytics = manager.get_company_analytics('test_company')
        assert 'current_rankings' in analytics
        assert 'historical_performance' in analytics
        assert 'achievements' in analytics

    def test_get_market_analytics(self, sample_company):
        """Test getting market analytics."""
        manager = AnalyticsManager()

        companies_data = [sample_company.to_dict()]
        market_data = {'demand_level': 1000.0}

        analytics = manager.get_market_analytics(market_data, companies_data)

        assert 'market_overview' in analytics
        assert 'competition_analysis' in analytics
        assert 'market_share_distribution' in analytics

    def test_get_analytics_summary(self):
        """Test getting analytics summary."""
        manager = AnalyticsManager()

        summary = manager.get_analytics_summary()

        assert 'total_rounds_analyzed' in summary
        assert 'leaderboard_stats' in summary
        assert 'kpi_summary' in summary

    def test_set_ranking_weights(self):
        """Test setting ranking weights."""
        manager = AnalyticsManager()

        weights = RankingWeights(financial_weight=0.4, operational_weight=0.3, market_weight=0.2, customer_weight=0.1)
        manager.set_ranking_weights(weights)

        assert manager.ranking_system.weights.financial_weight == 0.4