import pytest
from modules.analytics.kpi_calculator import KPICalculator, KPIMetrics
from modules.analytics.ranking_system import RankingSystem, RankingCriteria, RankingWeights
from modules.analytics.report_generator import ReportGenerator
from modules.analytics.leaderboard import Leaderboard
from modules.analytics.analytics_manager import AnalyticsManager


class TestKPICalculator:
    """Test KPICalculator class."""

    def test_calculate_all_kpis(self, kpi_calculator, sample_company, sample_market_state):
        """Test calculating all KPIs."""
        competitor_data = [
            {'market_share': 0.2, 'financials': {'revenue': 80000, 'profit': 15000}},
            {'market_share': 0.18, 'financials': {'revenue': 70000, 'profit': 12000}}
        ]

        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index,
            'economic_indicators': sample_market_state.economic_indicators
        }

        metrics = kpi_calculator.calculate_all_kpis(sample_company, market_data, competitor_data)

        assert isinstance(metrics, KPIMetrics)
        assert hasattr(metrics, 'financial_kpis')
        assert hasattr(metrics, 'operational_kpis')
        assert hasattr(metrics, 'market_kpis')
        assert hasattr(metrics, 'customer_kpis')

        # Check that KPIs were calculated
        assert len(metrics.financial_kpis) > 0
        assert len(metrics.operational_kpis) > 0
        assert len(metrics.market_kpis) > 0
        assert len(metrics.customer_kpis) > 0

    def test_calculate_financial_kpis(self, kpi_calculator, sample_company):
        """Test financial KPI calculations."""
        financial_kpis = kpi_calculator._calculate_financial_kpis(sample_company)

        expected_kpis = [
            'profit_margin', 'gross_margin', 'return_on_assets', 'return_on_equity',
            'current_ratio', 'operating_cash_flow_ratio', 'cash_flow_margin'
        ]

        for kpi in expected_kpis:
            assert kpi in financial_kpis
            assert isinstance(financial_kpis[kpi], (int, float))

    def test_calculate_operational_kpis(self, kpi_calculator, sample_company):
        """Test operational KPI calculations."""
        operational_kpis = kpi_calculator._calculate_operational_kpis(sample_company)

        expected_kpis = [
            'capacity_utilization', 'operational_efficiency', 'production_efficiency',
            'quality_index', 'employee_productivity', 'asset_turnover'
        ]

        for kpi in expected_kpis:
            assert kpi in operational_kpis
            assert isinstance(operational_kpis[kpi], (int, float))

    def test_calculate_market_kpis(self, kpi_calculator, sample_company, sample_market_state):
        """Test market KPI calculations."""
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        competitor_data = [{'market_share': 0.2}, {'market_share': 0.18}]

        market_kpis = kpi_calculator._calculate_market_kpis(sample_company, market_data, competitor_data)

        expected_kpis = ['market_share', 'brand_value_index', 'competitive_position']

        for kpi in expected_kpis:
            assert kpi in market_kpis
            assert isinstance(market_kpis[kpi], (int, float))

    def test_calculate_customer_kpis(self, kpi_calculator, sample_company):
        """Test customer KPI calculations."""
        customer_kpis = kpi_calculator._calculate_customer_kpis(sample_company)

        expected_kpis = [
            'customer_satisfaction_score', 'customer_loyalty_index',
            'perceived_quality', 'retention_probability', 'recommendation_likelihood'
        ]

        for kpi in expected_kpis:
            assert kpi in customer_kpis
            assert isinstance(customer_kpis[kpi], (int, float))

    def test_get_kpi_trends(self, kpi_calculator, sample_company, sample_market_state):
        """Test getting KPI trends."""
        # Calculate KPIs multiple times to build history
        competitor_data = [{'market_share': 0.2}, {'market_share': 0.18}]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index,
            'economic_indicators': sample_market_state.economic_indicators
        }

        for _ in range(3):
            kpi_calculator.calculate_all_kpis(sample_company, market_data, competitor_data)

        trends = kpi_calculator.get_kpi_trends('profit_margin', periods=3)
        assert len(trends) == 3
        assert all(isinstance(value, float) for value in trends)

    def test_calculate_custom_kpi(self, kpi_calculator):
        """Test calculating custom KPIs."""
        data = {'revenue': 100000, 'costs': 80000, 'profit': 20000}

        # Test simple formula
        result = kpi_calculator.calculate_custom_kpi('margin', 'profit / revenue', data)
        assert result == 0.2

        # Test invalid formula
        result = kpi_calculator.calculate_custom_kpi('invalid', 'invalid syntax +++', data)
        assert result == 0.0


class TestRankingSystem:
    """Test RankingSystem class."""

    def test_ranking_system_creation(self):
        """Test creating a ranking system."""
        system = RankingSystem()
        assert system.weights is not None
        assert system.weights.validate()

    def test_custom_weights(self):
        """Test ranking system with custom weights."""
        custom_weights = RankingWeights(
            financial_weight=0.4,
            operational_weight=0.3,
            market_weight=0.2,
            customer_weight=0.1
        )

        system = RankingSystem(custom_weights)
        assert system.weights == custom_weights

    def test_invalid_weights(self):
        """Test ranking system with invalid weights."""
        invalid_weights = RankingWeights(
            financial_weight=0.5,
            operational_weight=0.3,
            market_weight=0.2,
            customer_weight=0.1  # Total = 1.1, invalid
        )

        with pytest.raises(ValueError, match="Ranking weights must sum to 1.0"):
            RankingSystem(invalid_weights)

    def test_rank_companies(self, ranking_system, sample_company):
        """Test ranking companies."""
        companies_data = [sample_company, sample_company]  # Same company twice for testing
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        rankings = ranking_system.rank_companies(companies_data, market_data)

        assert len(rankings) == 2
        assert all(isinstance(r, dict) for r in rankings)  # Should be converted to dict
        assert rankings[0]['rank'] == 1
        assert rankings[1]['rank'] == 2

    def test_ranking_criteria(self, ranking_system, sample_company):
        """Test different ranking criteria."""
        companies_data = [sample_company]
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        # Test different criteria
        for criteria in [RankingCriteria.FINANCIAL_PERFORMANCE,
                        RankingCriteria.OPERATIONAL_EFFICIENCY,
                        RankingCriteria.MARKET_POSITION,
                        RankingCriteria.CUSTOMER_SATISFACTION]:
            rankings = ranking_system.rank_companies(companies_data, market_data, criteria)
            assert len(rankings) == 1
            assert rankings[0]['score'] >= 0

    def test_get_peer_comparison(self, ranking_system, sample_company):
        """Test getting peer comparison."""
        companies_data = [sample_company, sample_company]
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        # Rank companies first
        ranking_system.rank_companies(companies_data, market_data)

        comparison = ranking_system.get_peer_comparison(sample_company.id)

        assert 'company_score' in comparison
        assert 'company_rank' in comparison
        assert 'total_companies' in comparison
        assert 'peer_average' in comparison

    def test_get_historical_performance(self, ranking_system, sample_company):
        """Test getting historical performance."""
        companies_data = [sample_company]
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        # Create some ranking history
        for _ in range(3):
            ranking_system.rank_companies(companies_data, market_data)

        history = ranking_system.get_historical_performance(sample_company.id)

        assert len(history) >= 2  # Should have multiple entries
        for entry in history:
            assert 'date' in entry
            assert 'rank' in entry
            assert 'score' in entry

    def test_get_top_performers(self, ranking_system, sample_company):
        """Test getting top performers."""
        companies_data = [sample_company, sample_company]
        market_data = {'demand_level': 1000.0, 'price_index': 1.0}

        ranking_system.rank_companies(companies_data, market_data)

        top_performers = ranking_system.get_top_performers(top_n=1)
        assert len(top_performers) == 1
        assert top_performers[0]['rank'] == 1


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_report_generator_creation(self, tmp_path):
        """Test creating a report generator."""
        reports_dir = tmp_path / "reports"
        generator = ReportGenerator(str(reports_dir))

        assert generator.output_dir == reports_dir

    def test_generate_simulation_report(self, report_generator, sample_simulation_state):
        """Test generating a simulation report."""
        report_path = report_generator.generate_simulation_report(sample_simulation_state)

        assert report_path.endswith('.json')

        # Verify file was created and contains expected data
        import json
        with open(report_path, 'r') as f:
            report_data = json.load(f)

        assert 'report_type' in report_data
        assert 'generated_at' in report_data

    def test_generate_kpi_report(self, report_generator, sample_company, sample_market_state):
        """Test generating a KPI report."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }

        report_path = report_generator.generate_kpi_report(companies_data, market_data)

        assert report_path.endswith('.json')

        import json
        with open(report_path, 'r') as f:
            report_data = json.load(f)

        assert 'kpi_data' in report_data
        assert 'summary_statistics' in report_data
        assert len(report_data['kpi_data']) == 1

    def test_generate_ranking_report(self, report_generator, sample_company, sample_market_state):
        """Test generating a ranking report."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }

        report_path = report_generator.generate_ranking_report(companies_data, market_data)

        assert report_path.endswith('.json')

        import json
        with open(report_path, 'r') as f:
            report_data = json.load(f)

        assert 'rankings' in report_data
        assert 'ranking_criteria' in report_data
        assert len(report_data['rankings']) == 1

    def test_generate_csv_report(self, report_generator):
        """Test generating a CSV report."""
        test_data = [
            {'name': 'Company A', 'revenue': 100000, 'profit': 20000},
            {'name': 'Company B', 'revenue': 120000, 'profit': 25000}
        ]

        csv_path = report_generator.generate_csv_report(test_data, "test_report")

        assert csv_path.endswith('.csv')

        with open(csv_path, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 3  # Header + 2 data rows
        assert lines[0].startswith('name,revenue,profit')


class TestLeaderboard:
    """Test Leaderboard class."""

    def test_leaderboard_creation(self, tmp_path):
        """Test creating a leaderboard."""
        persistence_file = tmp_path / "test_leaderboard.json"
        leaderboard = Leaderboard(str(persistence_file))

        assert len(leaderboard.leaderboards) > 0
        assert len(leaderboard.achievements) > 0

    def test_update_leaderboard(self, leaderboard, sample_company, sample_market_state):
        """Test updating leaderboard."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }

        entries = leaderboard.update_leaderboard(companies_data, market_data, 'overall')

        assert len(entries) == 1
        assert entries[0].company_id == sample_company.id
        assert entries[0].rank == 1

    def test_get_leaderboard(self, leaderboard, sample_company, sample_market_state):
        """Test getting leaderboard entries."""
        # First update the leaderboard
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        leaderboard.update_leaderboard(companies_data, market_data)

        entries = leaderboard.get_leaderboard('overall', limit=10)

        assert len(entries) == 1
        assert entries[0]['company_id'] == sample_company.id

    def test_get_company_rank(self, leaderboard, sample_company, sample_market_state):
        """Test getting company rank."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        leaderboard.update_leaderboard(companies_data, market_data)

        rank_entry = leaderboard.get_company_rank(sample_company.id, 'overall')

        assert rank_entry is not None
        assert rank_entry.company_id == sample_company.id
        assert rank_entry.rank == 1

    def test_check_achievements(self, leaderboard, sample_company):
        """Test checking achievements."""
        kpi_data = {'profit_margin': 0.25, 'market_share': 0.20}  # High values to trigger achievements

        achievements = leaderboard.check_achievements(sample_company, kpi_data)

        # Should have unlocked some achievements
        assert isinstance(achievements, list)

    def test_get_leaderboard_stats(self, leaderboard, sample_company, sample_market_state):
        """Test getting leaderboard statistics."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        leaderboard.update_leaderboard(companies_data, market_data)

        stats = leaderboard.get_leaderboard_stats()

        assert 'total_categories' in stats
        assert 'categories' in stats
        assert 'overall' in stats['categories']

    def test_export_leaderboard(self, leaderboard, sample_company, sample_market_state):
        """Test exporting leaderboard."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        leaderboard.update_leaderboard(companies_data, market_data)

        # Test JSON export
        json_data = leaderboard.export_leaderboard('overall', 'json')
        assert isinstance(json_data, str)
        assert 'rank' in json_data
        assert 'company_name' in json_data

        # Test CSV export
        csv_data = leaderboard.export_leaderboard('overall', 'csv')
        assert isinstance(csv_data, str)
        assert 'Rank,Company Name,Score' in csv_data


class TestAnalyticsManager:
    """Test AnalyticsManager class."""

    def test_analytics_manager_creation(self, tmp_path):
        """Test creating an analytics manager."""
        analytics_dir = tmp_path / "analytics"
        manager = AnalyticsManager({'output_dir': str(analytics_dir)})

        assert manager.output_dir == str(analytics_dir)
        assert manager.kpi_calculator is not None
        assert manager.ranking_system is not None
        assert manager.report_generator is not None
        assert manager.leaderboard is not None

    def test_process_round_analytics(self, analytics_manager, sample_company, sample_market_state):
        """Test processing round analytics."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index,
            'economic_indicators': sample_market_state.economic_indicators
        }

        results = analytics_manager.process_round_analytics(companies_data, market_data, 1)

        assert 'round_number' in results
        assert 'kpi_analysis' in results
        assert 'rankings' in results
        assert 'leaderboard_updates' in results

        assert results['round_number'] == 1
        assert len(results['kpi_analysis']) == 1

    def test_generate_comprehensive_report(self, analytics_manager, sample_simulation_state):
        """Test generating comprehensive report."""
        report_path = analytics_manager.generate_comprehensive_report(sample_simulation_state)

        assert report_path.endswith('.json')

        import json
        with open(report_path, 'r') as f:
            report_data = json.load(f)

        assert 'report_type' in report_data
        assert report_data['report_type'] == 'comprehensive'

    def test_get_company_analytics(self, analytics_manager, sample_company, sample_market_state):
        """Test getting company analytics."""
        # First process some analytics
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        analytics_manager.process_round_analytics(companies_data, market_data, 1)

        analytics = analytics_manager.get_company_analytics(sample_company.id)

        assert 'company_id' in analytics
        assert 'current_rankings' in analytics
        assert 'historical_performance' in analytics
        assert 'achievements' in analytics

    def test_get_market_analytics(self, analytics_manager, sample_company, sample_market_state):
        """Test getting market analytics."""
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index,
            'competition_intensity': sample_market_state.competition_intensity
        }

        analytics = analytics_manager.get_market_analytics(market_data, companies_data)

        assert 'market_overview' in analytics
        assert 'competition_analysis' in analytics
        assert 'market_share_distribution' in analytics

    def test_set_ranking_weights(self, analytics_manager):
        """Test setting custom ranking weights."""
        custom_weights = RankingWeights(0.4, 0.3, 0.2, 0.1)
        analytics_manager.set_ranking_weights(custom_weights)

        assert analytics_manager.ranking_system.weights == custom_weights

    def test_get_analytics_summary(self, analytics_manager, sample_company, sample_market_state):
        """Test getting analytics summary."""
        # Process some analytics first
        companies_data = [sample_company]
        market_data = {
            'demand_level': sample_market_state.demand_level,
            'price_index': sample_market_state.price_index
        }
        analytics_manager.process_round_analytics(companies_data, market_data, 1)

        summary = analytics_manager.get_analytics_summary()

        assert 'total_rounds_analyzed' in summary
        assert 'leaderboard_stats' in summary
        assert 'kpi_summary' in summary
        assert summary['total_rounds_analyzed'] == 1