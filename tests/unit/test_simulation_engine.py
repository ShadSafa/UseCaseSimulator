import pytest
from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.core.simulation_state import SimulationState


class TestSimulationConfig:
    """Test SimulationConfig dataclass."""

    def test_simulation_config_creation(self):
        """Test creating SimulationConfig with default values."""
        config = SimulationConfig()
        assert config.max_rounds == 10
        assert config.num_competitors == 3
        assert config.initial_market_demand == 1000.0
        assert config.market_volatility == 0.1
        assert config.event_frequency == 0.3

    def test_simulation_config_custom_values(self):
        """Test creating SimulationConfig with custom values."""
        config = SimulationConfig(
            max_rounds=20,
            num_competitors=5,
            initial_market_demand=1500.0,
            market_volatility=0.2,
            event_frequency=0.4
        )
        assert config.max_rounds == 20
        assert config.num_competitors == 5
        assert config.initial_market_demand == 1500.0
        assert config.market_volatility == 0.2
        assert config.event_frequency == 0.4


class TestSimulationEngine:
    """Test SimulationEngine class."""

    def test_simulation_engine_creation(self, simulation_config):
        """Test creating a simulation engine."""
        engine = SimulationEngine(simulation_config)
        assert engine.config == simulation_config
        assert engine.current_state is None
        assert engine.simulation_history == []

    def test_initialize_simulation(self, simulation_engine):
        """Test initializing a simulation."""
        state = simulation_engine.initialize_simulation()

        assert isinstance(state, SimulationState)
        assert state.round_number == 0
        assert state.player_company is not None
        assert state.market is not None
        assert len(state.competitors) == 3  # Default competitors
        assert state.events == []
        assert isinstance(state.kpis, dict)

        # Check that engine state was set
        assert simulation_engine.current_state == state
        assert len(simulation_engine.simulation_history) == 1

    def test_run_round_without_initialization(self, simulation_engine, player_decisions):
        """Test running a round without initialization."""
        with pytest.raises(ValueError, match="Simulation not initialized"):
            simulation_engine.run_round(player_decisions)

    def test_run_round_basic(self, initialized_simulation_engine, player_decisions):
        """Test running a basic simulation round."""
        initial_round = initialized_simulation_engine.current_state.round_number

        results = initialized_simulation_engine.run_round(player_decisions)

        assert 'round_number' in results
        assert 'round_results' in results
        assert 'triggered_events' in results
        assert 'expired_events' in results
        assert 'game_state' in results
        assert 'is_simulation_over' in results

        assert results['round_number'] == initial_round + 1
        assert isinstance(results['round_results'], dict)
        assert isinstance(results['triggered_events'], list)

    def test_run_round_updates_state(self, initialized_simulation_engine, player_decisions):
        """Test that running a round updates the simulation state."""
        initial_company_revenue = initialized_simulation_engine.current_state.player_company.financial_data.revenue

        results = initialized_simulation_engine.run_round(player_decisions)

        # Check that company state was updated
        updated_company = initialized_simulation_engine.current_state.player_company
        assert updated_company.financial_data.revenue != initial_company_revenue

        # Check that round number was incremented
        assert initialized_simulation_engine.current_state.round_number == 1

        # Check that history was updated
        assert len(initialized_simulation_engine.simulation_history) == 2

    def test_get_current_state(self, initialized_simulation_engine):
        """Test getting current simulation state."""
        state = initialized_simulation_engine.get_current_state()
        assert isinstance(state, SimulationState)
        assert state == initialized_simulation_engine.current_state

    def test_get_current_state_uninitialized(self, simulation_engine):
        """Test getting current state when uninitialized."""
        state = simulation_engine.get_current_state()
        assert state is None

    def test_simulation_termination(self, short_simulation_config, player_decisions):
        """Test simulation termination after max rounds."""
        engine = SimulationEngine(short_simulation_config)
        engine.initialize_simulation()

        # Run rounds until simulation should end
        for round_num in range(1, short_simulation_config.max_rounds + 1):
            results = engine.run_round(player_decisions)
            expected_over = (round_num >= short_simulation_config.max_rounds)
            assert results['is_simulation_over'] == expected_over

    def test_save_simulation(self, initialized_simulation_engine, tmp_path):
        """Test saving simulation to file."""
        save_path = tmp_path / "test_save.json"

        # Save simulation
        result_path = initialized_simulation_engine.save_simulation(str(save_path))

        assert result_path == str(save_path)
        assert save_path.exists()

        # Verify save file contents
        import json
        with open(save_path, 'r') as f:
            save_data = json.load(f)

        assert 'simulation_config' in save_data
        assert 'current_state' in save_data
        assert 'round_manager' in save_data
        assert 'event_manager' in save_data
        assert 'simulation_history' in save_data

    def test_load_simulation(self, simulation_engine, initialized_simulation_engine, tmp_path):
        """Test loading simulation from file."""
        # First save a simulation
        save_path = tmp_path / "test_save.json"
        initialized_simulation_engine.save_simulation(str(save_path))

        # Now load it into a new engine
        loaded_engine = simulation_engine.load_simulation(str(save_path))

        assert isinstance(loaded_engine, SimulationEngine)
        assert loaded_engine.current_state is not None
        assert loaded_engine.current_state.round_number == initialized_simulation_engine.current_state.round_number
        assert loaded_engine.current_state.player_company.id == initialized_simulation_engine.current_state.player_company.id

    def test_load_simulation_invalid_file(self, simulation_engine):
        """Test loading simulation from invalid file."""
        with pytest.raises(FileNotFoundError):
            simulation_engine.load_simulation("nonexistent_file.json")

    def test_get_simulation_summary_uninitialized(self, simulation_engine):
        """Test getting simulation summary when uninitialized."""
        summary = simulation_engine.get_simulation_summary()
        assert summary['status'] == 'no_active_simulation'

    def test_get_simulation_summary_initialized(self, initialized_simulation_engine):
        """Test getting simulation summary when initialized."""
        summary = initialized_simulation_engine.get_simulation_summary()

        required_fields = [
            'current_round', 'max_rounds', 'is_simulation_over',
            'total_events', 'active_events', 'kpis', 'simulation_history_length'
        ]

        for field in required_fields:
            assert field in summary

    def test_quick_save(self, initialized_simulation_engine, tmp_path):
        """Test quick save functionality."""
        save_path = initialized_simulation_engine.quick_save()

        assert save_path is not None
        assert "quicksave" in save_path

        # Verify file exists
        import os
        assert os.path.exists(save_path)

    def test_auto_save(self, initialized_simulation_engine):
        """Test auto save functionality."""
        # Should not auto-save on round 0
        save_path = initialized_simulation_engine.auto_save(5)
        assert save_path is None

        # Run to round 5
        for _ in range(5):
            initialized_simulation_engine.run_round({})

        # Should auto-save on round 5
        save_path = initialized_simulation_engine.auto_save(5)
        assert save_path is not None
        assert "autosave_round_5" in save_path

    def test_list_simulation_saves(self, initialized_simulation_engine, tmp_path):
        """Test listing simulation saves."""
        # Create some save files
        save_dir = tmp_path / "saves"
        save_dir.mkdir()

        # Temporarily change the serializer base path
        original_base = initialized_simulation_engine.serializer.base_path
        initialized_simulation_engine.serializer.base_path = save_dir

        try:
            # Save a few simulations
            initialized_simulation_engine.save_simulation("manual_save_1")
            initialized_simulation_engine.quick_save()
            initialized_simulation_engine.run_round({})
            save_path = initialized_simulation_engine.auto_save(1)
            if save_path:
                # Copy auto save to our test directory
                import shutil
                shutil.copy(save_path, save_dir / "autosave_round_1.json")

            saves = initialized_simulation_engine.list_simulation_saves()

            assert len(saves) >= 2  # At least manual and quick saves

            # Check save types
            save_types = [s['save_type'] for s in saves]
            assert 'manual_save' in save_types
            assert 'quick_save' in save_types

        finally:
            initialized_simulation_engine.serializer.base_path = original_base

    def test_delete_simulation_save(self, initialized_simulation_engine, tmp_path):
        """Test deleting simulation saves."""
        save_path = tmp_path / "test_delete.json"
        initialized_simulation_engine.save_simulation(str(save_path))

        # Delete the save
        result = initialized_simulation_engine.delete_simulation_save("test_delete")
        assert result is True

        # Verify file is gone
        assert not save_path.exists()

    def test_delete_nonexistent_save(self, initialized_simulation_engine):
        """Test deleting nonexistent save."""
        result = initialized_simulation_engine.delete_simulation_save("nonexistent")
        assert result is False

    def test_export_simulation_to_csv(self, initialized_simulation_engine, tmp_path):
        """Test exporting simulation data to CSV."""
        # Add some history
        for _ in range(3):
            initialized_simulation_engine.run_round({})

        csv_path = tmp_path / "simulation_export.csv"
        result_path = initialized_simulation_engine.export_simulation_to_csv(str(csv_path))

        assert result_path == str(csv_path)
        assert csv_path.exists()

        # Verify CSV content
        with open(csv_path, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 4  # Header + initial + 3 rounds
        assert lines[0].startswith("Round,Revenue,Costs,Profit")  # Header

    def test_get_save_file_summary(self, initialized_simulation_engine, tmp_path):
        """Test getting save file summary."""
        save_path = tmp_path / "summary_test.json"
        initialized_simulation_engine.save_simulation(str(save_path))

        summary = initialized_simulation_engine.get_save_file_summary("summary_test")

        required_fields = [
            'filename', 'save_type', 'round_number', 'company_name',
            'saved_at', 'version', 'has_company_data', 'has_market_data',
            'has_competitors', 'simulation_complete'
        ]

        for field in required_fields:
            assert field in summary

    def test_cleanup_old_saves(self, initialized_simulation_engine, tmp_path):
        """Test cleaning up old auto saves."""
        save_dir = tmp_path / "saves"
        save_dir.mkdir()

        original_base = initialized_simulation_engine.serializer.base_path
        initialized_simulation_engine.serializer.base_path = save_dir

        try:
            # Create multiple auto saves
            for i in range(15):
                initialized_simulation_engine.run_round({})
                save_path = initialized_simulation_engine.auto_save(1)
                if save_path and i > 0:  # Skip first round
                    import shutil
                    shutil.copy(save_path, save_dir / f"autosave_round_{i}.json")

            # Clean up keeping only 5 most recent
            deleted_count = initialized_simulation_engine.cleanup_old_saves(keep_recent=5, save_type='auto_save')

            assert deleted_count >= 5  # Should have deleted some files

        finally:
            initialized_simulation_engine.serializer.base_path = original_base


class TestSimulationEngineIntegration:
    """Integration tests for SimulationEngine."""

    def test_full_simulation_run(self, short_simulation_config, player_decisions):
        """Test running a complete simulation."""
        engine = SimulationEngine(short_simulation_config)
        engine.initialize_simulation()

        round_results = []
        for round_num in range(1, short_simulation_config.max_rounds + 1):
            results = engine.run_round(player_decisions)
            round_results.append(results)

            assert results['round_number'] == round_num
            assert not results['is_simulation_over'] or round_num == short_simulation_config.max_rounds

        # Final round should end simulation
        final_results = round_results[-1]
        assert final_results['is_simulation_over']

    def test_simulation_state_persistence(self, initialized_simulation_engine, tmp_path, player_decisions):
        """Test that simulation state persists correctly across saves/loads."""
        # Run a few rounds
        for _ in range(3):
            initialized_simulation_engine.run_round(player_decisions)

        original_state = initialized_simulation_engine.current_state

        # Save and reload
        save_path = tmp_path / "persistence_test.json"
        initialized_simulation_engine.save_simulation(str(save_path))

        new_engine = SimulationEngine()
        loaded_engine = new_engine.load_simulation(str(save_path))

        # Compare key state elements
        assert loaded_engine.current_state.round_number == original_state.round_number
        assert loaded_engine.current_state.player_company.financial_data.revenue == original_state.player_company.financial_data.revenue
        assert loaded_engine.current_state.market.state.demand_level == original_state.market.state.demand_level
        assert len(loaded_engine.current_state.competitors) == len(original_state.competitors)

    def test_event_system_integration(self, simulation_with_events, player_decisions):
        """Test integration with event system."""
        # Run a round and check that events are processed
        results = simulation_with_events.run_round(player_decisions)

        assert 'triggered_events' in results
        assert 'expired_events' in results

        # Check that active events were processed
        assert len(simulation_with_events.event_manager.get_active_events()) <= 2  # May have expired

    def test_market_integration(self, initialized_simulation_engine, player_decisions):
        """Test integration with market system."""
        initial_market_state = initialized_simulation_engine.current_state.market.get_market_state()

        # Run a round
        results = initialized_simulation_engine.run_round(player_decisions)

        # Market should have advanced
        updated_market_state = initialized_simulation_engine.current_state.market.get_market_state()
        assert updated_market_state != initial_market_state  # State should have changed

    def test_company_decision_integration(self, initialized_simulation_engine):
        """Test integration of company decisions."""
        # Test price change decision
        decisions = {'price_change': {'new_price': 105.0}}
        results = initialized_simulation_engine.run_round(decisions)

        assert results['round_number'] == 1

        # Test capacity expansion
        decisions = {'capacity_expansion': {'expansion_amount': 200.0}}
        results = initialized_simulation_engine.run_round(decisions)

        company = initialized_simulation_engine.current_state.player_company
        assert company.operations_data.capacity > 1000.0  # Should have increased from default