import pytest
import json
import os
from pathlib import Path
from modules.persistence.data_serializer import DataSerializer
from modules.persistence.company_persistence import CompanyPersistence
from modules.persistence.market_persistence import MarketPersistence
from modules.persistence.simulation_persistence import SimulationPersistence


class TestDataSerializer:
    """Test DataSerializer class."""

    def test_serializer_creation(self, tmp_path):
        """Test creating a data serializer."""
        save_dir = tmp_path / "saves"
        serializer = DataSerializer(str(save_dir))

        assert serializer.base_path == save_dir

    def test_serialize_deserialize_json(self, data_serializer, sample_company):
        """Test JSON serialization and deserialization."""
        # Serialize
        save_path = data_serializer.serialize_to_json(sample_company.to_dict(), "test_company")

        assert save_path.endswith("test_company.json")
        assert os.path.exists(save_path)

        # Deserialize
        loaded_data = data_serializer.deserialize_from_json("test_company")

        assert loaded_data['id'] == sample_company.id
        assert loaded_data['name'] == sample_company.name

    def test_serialize_deserialize_pickle(self, data_serializer, sample_company):
        """Test pickle serialization and deserialization."""
        # Serialize
        save_path = data_serializer.serialize_to_pickle(sample_company, "test_company_pickle")

        assert save_path.endswith("test_company_pickle.pkl")
        assert os.path.exists(save_path)

        # Deserialize
        loaded_data = data_serializer.deserialize_from_pickle("test_company_pickle")

        assert loaded_data.id == sample_company.id
        assert loaded_data.name == sample_company.name

    def test_list_save_files(self, data_serializer, sample_company):
        """Test listing save files."""
        # Create some save files
        data_serializer.serialize_to_json(sample_company.to_dict(), "company1")
        data_serializer.serialize_to_json(sample_company.to_dict(), "company2")
        data_serializer.serialize_to_pickle(sample_company, "company_pickle")

        json_files = data_serializer.list_save_files("json")
        pickle_files = data_serializer.list_save_files("pickle")

        assert "company1" in json_files
        assert "company2" in json_files
        assert "company_pickle" in pickle_files

    def test_delete_save_file(self, data_serializer, sample_company):
        """Test deleting save files."""
        data_serializer.serialize_to_json(sample_company.to_dict(), "delete_test")

        # Verify file exists
        assert os.path.exists(data_serializer.base_path / "delete_test.json")

        # Delete file
        result = data_serializer.delete_save_file("delete_test", "json")
        assert result is True

        # Verify file is gone
        assert not os.path.exists(data_serializer.base_path / "delete_test.json")

    def test_get_file_info(self, data_serializer, sample_company):
        """Test getting file information."""
        data_serializer.serialize_to_json(sample_company.to_dict(), "info_test")

        info = data_serializer.get_file_info("info_test", "json")

        assert info is not None
        assert info['filename'] == "info_test"
        assert info['extension'] == "json"
        assert 'size_bytes' in info
        assert 'modified_time' in info

    def test_validate_save_data(self, data_serializer, sample_company):
        """Test save data validation."""
        company_data = sample_company.to_dict()

        # Valid company data
        assert data_serializer.validate_save_data(company_data, "company")

        # Invalid data
        invalid_data = {"invalid": "data"}
        assert not data_serializer.validate_save_data(invalid_data, "company")

        # Unknown data type
        assert not data_serializer.validate_save_data(company_data, "unknown")

    def test_create_backup(self, data_serializer, sample_company):
        """Test creating file backups."""
        data_serializer.serialize_to_json(sample_company.to_dict(), "backup_test")

        backup_path = data_serializer.create_backup("backup_test", "json")

        assert backup_path is not None
        assert "backup" in backup_path
        assert os.path.exists(backup_path)

        # Original file should still exist
        assert os.path.exists(data_serializer.base_path / "backup_test.json")


class TestCompanyPersistence:
    """Test CompanyPersistence class."""

    def test_company_persistence_creation(self):
        """Test creating company persistence."""
        persistence = CompanyPersistence()
        assert persistence.serializer is not None

    def test_save_load_company(self, company_persistence, sample_company):
        """Test saving and loading a company."""
        # Save company
        save_path = company_persistence.save_company(sample_company, "test_save")

        assert save_path.endswith("test_save.json")
        assert os.path.exists(save_path)

        # Load company
        loaded_company = company_persistence.load_company("test_save")

        assert loaded_company.id == sample_company.id
        assert loaded_company.name == sample_company.name
        assert loaded_company.financial_data.revenue == sample_company.financial_data.revenue

    def test_save_multiple_companies(self, company_persistence, sample_company, established_company):
        """Test saving multiple companies."""
        companies = [sample_company, established_company]

        save_path = company_persistence.save_multiple_companies(companies, "multi_test")

        assert save_path.endswith("multi_test.json")
        assert os.path.exists(save_path)

        # Load and verify
        loaded_companies = company_persistence.load_multiple_companies("multi_test")

        assert len(loaded_companies) == 2
        assert loaded_companies[0].id == sample_company.id
        assert loaded_companies[1].id == established_company.id

    def test_save_company_snapshot(self, company_persistence, sample_company):
        """Test saving company snapshots."""
        snapshot_path = company_persistence.save_company_snapshot(sample_company, 5)

        assert "round_5" in snapshot_path
        assert os.path.exists(snapshot_path)

    def test_list_company_saves(self, company_persistence, sample_company):
        """Test listing company saves."""
        company_persistence.save_company(sample_company, "list_test1")
        company_persistence.save_company(sample_company, "list_test2")

        saves = company_persistence.list_company_saves()

        assert len(saves) >= 2
        filenames = [s['filename'] for s in saves]
        assert "list_test1" in filenames
        assert "list_test2" in filenames

    def test_find_company_snapshots(self, company_persistence, sample_company):
        """Test finding company snapshots."""
        company_persistence.save_company_snapshot(sample_company, 3)
        company_persistence.save_company_snapshot(sample_company, 5)
        company_persistence.save_company_snapshot(sample_company, 7)

        snapshots = company_persistence.find_company_snapshots(sample_company.id)

        assert len(snapshots) == 3
        round_numbers = [s['round_number'] for s in snapshots]
        assert 3 in round_numbers
        assert 5 in round_numbers
        assert 7 in round_numbers

    def test_export_company_to_csv(self, company_persistence, sample_company):
        """Test exporting company data to CSV."""
        csv_path = company_persistence.export_company_to_csv(sample_company, "csv_test")

        assert csv_path.endswith("csv_test.csv")
        assert os.path.exists(csv_path)

        with open(csv_path, 'r') as f:
            lines = f.readlines()

        assert len(lines) > 1  # At least header + data
        assert lines[0].startswith("Category,Metric,Value")

    def test_get_company_backup(self, company_persistence, sample_company):
        """Test creating company backups."""
        company_persistence.save_company(sample_company, "backup_test")

        backup_path = company_persistence.get_company_backup(sample_company.id)

        assert backup_path is not None
        assert "backup" in backup_path
        assert os.path.exists(backup_path)


class TestMarketPersistence:
    """Test MarketPersistence class."""

    def test_market_persistence_creation(self):
        """Test creating market persistence."""
        persistence = MarketPersistence()
        assert persistence.serializer is not None

    def test_save_load_market(self, market_persistence, sample_market):
        """Test saving and loading a market."""
        # Save market
        save_path = market_persistence.save_market(sample_market, "test_market")

        assert save_path.endswith("test_market.json")
        assert os.path.exists(save_path)

        # Load market
        loaded_market = market_persistence.load_market("test_market")

        assert loaded_market.round_number == sample_market.round_number
        assert loaded_market.state.demand_level == sample_market.state.demand_level

    def test_save_market_snapshot(self, market_persistence, sample_market):
        """Test saving market snapshots."""
        snapshot_path = market_persistence.save_market_snapshot(sample_market)

        assert f"round_{sample_market.round_number}" in snapshot_path
        assert os.path.exists(snapshot_path)

    def test_list_market_saves(self, market_persistence, sample_market):
        """Test listing market saves."""
        market_persistence.save_market(sample_market, "market_test1")
        market_persistence.save_market(sample_market, "market_test2")

        saves = market_persistence.list_market_saves()

        assert len(saves) >= 2
        filenames = [s['filename'] for s in saves]
        assert "market_test1" in filenames or "market_test1" in [s['filename'] for s in saves]

    def test_find_market_snapshots(self, market_persistence, sample_market):
        """Test finding market snapshots by round range."""
        # Advance market to different rounds and save
        original_round = sample_market.round_number

        for round_num in [5, 10, 15]:
            sample_market.round_number = round_num
            market_persistence.save_market_snapshot(sample_market)

        # Reset round number
        sample_market.round_number = original_round

        # Find snapshots in range
        snapshots = market_persistence.find_market_snapshots(8, 12)

        assert len(snapshots) == 1
        assert snapshots[0]['round_number'] == 10

    def test_export_market_to_csv(self, market_persistence, sample_market):
        """Test exporting market data to CSV."""
        csv_path = market_persistence.export_market_to_csv(sample_market, "market_csv_test")

        assert csv_path.endswith("market_csv_test.csv")
        assert os.path.exists(csv_path)

        with open(csv_path, 'r') as f:
            lines = f.readlines()

        assert len(lines) > 1
        assert lines[0].startswith("Category,Metric,Value")

    def test_get_market_backup(self, market_persistence, sample_market):
        """Test creating market backups."""
        market_persistence.save_market(sample_market, "market_backup_test")

        backup_path = market_persistence.get_market_backup(sample_market.round_number)

        assert backup_path is not None
        assert "backup" in backup_path
        assert os.path.exists(backup_path)

    def test_save_load_market_scenario(self, market_persistence, sample_market):
        """Test saving and loading market scenarios."""
        scenario_name = "test_scenario"

        # Save as scenario
        save_path = market_persistence.save_market_scenario(sample_market, scenario_name)
        assert save_path.endswith(f"{scenario_name}.json")

        # Load scenario
        loaded_market = market_persistence.load_market_scenario(scenario_name)

        assert loaded_market.round_number == sample_market.round_number
        assert loaded_market.state.demand_level == sample_market.state.demand_level

    def test_list_market_scenarios(self, market_persistence, sample_market):
        """Test listing market scenarios."""
        scenarios = ["scenario_a", "scenario_b", "scenario_c"]

        for scenario in scenarios:
            market_persistence.save_market_scenario(sample_market, scenario)

        listed_scenarios = market_persistence.list_market_scenarios()

        for scenario in scenarios:
            assert scenario in listed_scenarios

    def test_get_market_history(self, market_persistence, sample_market):
        """Test getting market history."""
        # Create some historical data
        for round_num in range(1, 6):
            sample_market.round_number = round_num
            market_persistence.save_market_snapshot(sample_market)

        history = market_persistence.get_market_history(max_rounds=3)

        assert len(history) == 3  # Limited to 3 most recent

    def test_compare_market_states(self, market_persistence, sample_market):
        """Test comparing market states between rounds."""
        # Save market at round 5
        sample_market.round_number = 5
        market_persistence.save_market_snapshot(sample_market)

        # Modify and save at round 10
        sample_market.round_number = 10
        sample_market.state.demand_level = 1200.0
        market_persistence.save_market_snapshot(sample_market)

        # Compare
        comparison = market_persistence.compare_market_states(5, 10)

        assert 'demand_change' in comparison
        assert comparison['demand_change'] == 200.0  # 1200 - 1000


class TestSimulationPersistence:
    """Test SimulationPersistence class."""

    def test_simulation_persistence_creation(self):
        """Test creating simulation persistence."""
        persistence = SimulationPersistence()
        assert persistence.serializer is not None
        assert persistence.company_persistence is not None
        assert persistence.market_persistence is not None

    def test_save_load_simulation(self, simulation_persistence, initialized_simulation_engine):
        """Test saving and loading a complete simulation."""
        # Save simulation
        save_path = simulation_persistence.save_simulation(initialized_simulation_engine, "sim_test")

        assert save_path.endswith("sim_test.json")
        assert os.path.exists(save_path)

        # Load simulation
        loaded_engine = simulation_persistence.load_simulation("sim_test")

        assert isinstance(loaded_engine, type(initialized_simulation_engine))
        assert loaded_engine.current_state.round_number == initialized_simulation_engine.current_state.round_number
        assert loaded_engine.current_state.player_company.id == initialized_simulation_engine.current_state.player_company.id

    def test_save_simulation_snapshot(self, simulation_persistence, initialized_simulation_engine):
        """Test saving simulation snapshots."""
        snapshot_path = simulation_persistence.save_simulation_snapshot(initialized_simulation_engine)

        assert f"round_{initialized_simulation_engine.current_state.round_number}" in snapshot_path
        assert os.path.exists(snapshot_path)

    def test_quick_save(self, simulation_persistence, initialized_simulation_engine):
        """Test quick save functionality."""
        save_path = simulation_persistence.quick_save(initialized_simulation_engine)

        assert save_path is not None
        assert "quicksave" in save_path
        assert os.path.exists(save_path)

    def test_auto_save(self, simulation_persistence, initialized_simulation_engine):
        """Test auto save functionality."""
        # Should not auto-save on current round
        save_path = simulation_persistence.auto_save(initialized_simulation_engine, 5)
        assert save_path is None

        # Run to round 5
        for _ in range(5):
            initialized_simulation_engine.run_round({})

        # Should auto-save
        save_path = simulation_persistence.auto_save(initialized_simulation_engine, 5)
        assert save_path is not None
        assert "autosave_round_5" in save_path

    def test_list_simulation_saves(self, simulation_persistence, initialized_simulation_engine):
        """Test listing simulation saves."""
        simulation_persistence.save_simulation(initialized_simulation_engine, "manual_test")
        simulation_persistence.quick_save(initialized_simulation_engine)

        saves = simulation_persistence.list_simulation_saves()

        assert len(saves) >= 2
        save_types = [s['save_type'] for s in saves]
        assert 'manual_save' in save_types
        assert 'quick_save' in save_types

    def test_export_simulation_to_csv(self, simulation_persistence, initialized_simulation_engine):
        """Test exporting simulation data to CSV."""
        # Run a few rounds to have history
        for _ in range(3):
            initialized_simulation_engine.run_round({})

        csv_path = simulation_persistence.export_simulation_to_csv(initialized_simulation_engine, "sim_csv_test")

        assert csv_path.endswith("sim_csv_test.csv")
        assert os.path.exists(csv_path)

        with open(csv_path, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 5  # Header + initial + 3 rounds
        assert lines[0].startswith("Round,Revenue,Costs,Profit")

    def test_save_game_components_separately(self, simulation_persistence, initialized_simulation_engine):
        """Test saving game components separately."""
        base_filename = "components_test"

        saved_files = simulation_persistence.save_game_components_separately(
            initialized_simulation_engine, base_filename
        )

        assert 'company' in saved_files
        assert 'market' in saved_files
        assert 'competitors' in saved_files

        for file_path in saved_files.values():
            assert os.path.exists(file_path)

    def test_load_game_components_separately(self, simulation_persistence, initialized_simulation_engine):
        """Test loading game components separately."""
        base_filename = "load_components_test"

        # Save components first
        simulation_persistence.save_game_components_separately(
            initialized_simulation_engine, base_filename
        )

        # Load components
        components = simulation_persistence.load_game_components_separately(base_filename)

        assert 'company' in components
        assert 'market' in components
        assert 'competitors' in components

        assert components['company'].id == initialized_simulation_engine.current_state.player_company.id
        assert components['market'].round_number == initialized_simulation_engine.current_state.market.round_number

    def test_get_save_file_summary(self, simulation_persistence, initialized_simulation_engine):
        """Test getting save file summary."""
        simulation_persistence.save_simulation(initialized_simulation_engine, "summary_test")

        summary = simulation_persistence.get_save_file_summary("summary_test")

        required_fields = [
            'filename', 'save_type', 'round_number', 'company_name',
            'saved_at', 'version', 'has_company_data', 'has_market_data',
            'has_competitors', 'simulation_complete'
        ]

        for field in required_fields:
            assert field in summary

    def test_cleanup_old_saves(self, simulation_persistence, initialized_simulation_engine):
        """Test cleaning up old auto saves."""
        # Create multiple auto saves
        for i in range(15):
            initialized_simulation_engine.run_round({})
            simulation_persistence.auto_save(initialized_simulation_engine, 1)

        # Count auto saves before cleanup
        saves_before = simulation_persistence.list_simulation_saves()
        auto_saves_before = [s for s in saves_before if s['save_type'] == 'auto_save']

        # Clean up keeping only 5
        deleted_count = simulation_persistence.cleanup_old_saves(keep_recent=5, save_type='auto_save')

        # Verify cleanup
        saves_after = simulation_persistence.list_simulation_saves()
        auto_saves_after = [s for s in saves_after if s['save_type'] == 'auto_save']

        assert len(auto_saves_after) <= 5
        assert deleted_count >= 10  # Should have deleted most files