import unittest
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.core.simulation_state import SimulationState
from modules.core.round_manager import RoundManager
from modules.core.event_manager import EventManager, Event, EventType


class TestSimulationEngine(unittest.TestCase):
    """Test cases for the core simulation engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(max_rounds=5, num_competitors=2)
        self.engine = SimulationEngine(self.config)

    def test_initialization(self):
        """Test simulation initialization."""
        state = self.engine.initialize_simulation()

        self.assertIsInstance(state, SimulationState)
        self.assertEqual(state.round_number, 0)
        self.assertIsInstance(state.player_company, object)
        self.assertEqual(len(state.competitors), 2)
        self.assertIsInstance(state.kpis, dict)

    def test_round_progression(self):
        """Test basic round progression."""
        self.engine.initialize_simulation()

        # Test first round
        decisions = {
            'pricing': {'price': 120.0},
            'marketing': {'budget': 5000.0}
        }

        result = self.engine.run_round(decisions)

        self.assertEqual(result['round_number'], 1)
        self.assertIn('round_results', result)
        self.assertIn('game_state', result)
        self.assertFalse(result['is_simulation_over'])

        # Check that state was updated
        current_state = self.engine.get_current_state()
        self.assertEqual(current_state.round_number, 1)

    def test_multiple_rounds(self):
        """Test multiple round progression."""
        self.engine.initialize_simulation()

        for round_num in range(1, 4):
            decisions = {'pricing': {'price': 100.0 + round_num * 10}}
            result = self.engine.run_round(decisions)

            self.assertEqual(result['round_number'], round_num)
            self.assertFalse(result['is_simulation_over'])

        # Test final round
        result = self.engine.run_round({'pricing': {'price': 130.0}})
        self.assertEqual(result['round_number'], 4)
        self.assertFalse(result['is_simulation_over'])  # Still not over at round 4 of 5

        # Test game over
        result = self.engine.run_round({'pricing': {'price': 140.0}})
        self.assertEqual(result['round_number'], 5)
        self.assertTrue(result['is_simulation_over'])

    def test_event_system_integration(self):
        """Test that events are triggered and processed."""
        self.engine.initialize_simulation()

        # Run a few rounds to potentially trigger events
        for _ in range(3):
            result = self.engine.run_round({'pricing': {'price': 100.0}})
            # Events might or might not trigger based on probability
            self.assertIn('triggered_events', result)
            self.assertIn('expired_events', result)

    def test_save_load_simulation(self):
        """Test simulation save and load functionality."""
        # Initialize and run a round
        self.engine.initialize_simulation()
        self.engine.run_round({'pricing': {'price': 110.0}})

        # Save simulation
        save_success = self.engine.save_simulation('test_save')
        self.assertTrue(save_success)

        # Create new engine and load
        new_engine = SimulationEngine(self.config)
        loaded_state = new_engine.load_simulation('test_save')

        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.round_number, 1)

        # Clean up
        if os.path.exists('data/saves/test_save.json'):
            os.remove('data/saves/test_save.json')

    def test_simulation_summary(self):
        """Test simulation summary functionality."""
        summary = self.engine.get_simulation_summary()
        self.assertEqual(summary['status'], 'no_active_simulation')

        self.engine.initialize_simulation()
        summary = self.engine.get_simulation_summary()

        self.assertIn('current_round', summary)
        self.assertIn('max_rounds', summary)
        self.assertIn('is_simulation_over', summary)
        self.assertEqual(summary['current_round'], 0)
        self.assertEqual(summary['max_rounds'], 5)


class TestRoundManager(unittest.TestCase):
    """Test cases for RoundManager."""

    def setUp(self):
        self.manager = RoundManager(max_rounds=3)

    def test_round_advancement(self):
        """Test round advancement."""
        self.assertEqual(self.manager.get_current_round(), 0)

        self.assertEqual(self.manager.advance_round(), 1)
        self.assertEqual(self.manager.get_current_round(), 1)

        self.assertEqual(self.manager.advance_round(), 2)
        self.assertEqual(self.manager.get_current_round(), 2)

        self.assertEqual(self.manager.advance_round(), 3)
        self.assertEqual(self.manager.get_current_round(), 3)

        # Should not advance beyond max
        self.assertEqual(self.manager.advance_round(), 3)
        self.assertEqual(self.manager.get_current_round(), 3)

    def test_simulation_over(self):
        """Test simulation over detection."""
        self.assertFalse(self.manager.is_simulation_over())

        for _ in range(3):
            self.manager.advance_round()

        self.assertTrue(self.manager.is_simulation_over())

    def test_decision_processing(self):
        """Test decision processing."""
        decisions = {
            'pricing': {'price': 150.0},
            'investment': {'amount': 10000.0},
            'marketing': {'budget': 3000.0}
        }

        result = self.manager.process_decisions(decisions)

        self.assertIn('results', result)
        self.assertIn('pricing', result['results'])
        self.assertIn('investment', result['results'])
        self.assertIn('marketing', result['results'])

    def test_reset(self):
        """Test manager reset."""
        self.manager.advance_round()
        self.manager.advance_round()
        self.assertEqual(self.manager.get_current_round(), 2)

        self.manager.reset()
        self.assertEqual(self.manager.get_current_round(), 0)


class TestEventManager(unittest.TestCase):
    """Test cases for EventManager."""

    def setUp(self):
        self.manager = EventManager()

    def test_event_generation(self):
        """Test random event generation."""
        events = self.manager.generate_random_events(1)
        # Events may or may not be generated based on probability
        self.assertIsInstance(events, list)

        for event in events:
            self.assertIsInstance(event, Event)
            self.assertEqual(event.type, EventType.RANDOM)

    def test_scheduled_events(self):
        """Test scheduled event processing."""
        # Round 5 should trigger regulatory change
        events = self.manager.process_scheduled_events(5)
        regulatory_event = next((e for e in events if e.id == 'regulatory_change'), None)
        self.assertIsNotNone(regulatory_event)

        # Round 1 should not trigger it
        events = self.manager.process_scheduled_events(1)
        regulatory_event = next((e for e in events if e.id == 'regulatory_change'), None)
        self.assertIsNone(regulatory_event)

    def test_event_triggering(self):
        """Test event triggering and processing."""
        market_crash = self.manager.event_definitions['market_crash']

        event_data = self.manager.trigger_event(market_crash, 1)

        self.assertIn('event', event_data)
        self.assertEqual(event_data['triggered_round'], 1)
        self.assertEqual(event_data['remaining_duration'], 2)

        # Check active events
        active = self.manager.get_active_events()
        self.assertEqual(len(active), 1)

        # Process events
        expired = self.manager.process_active_events()
        self.assertEqual(len(expired), 0)  # Still active

        # Process again to expire
        expired = self.manager.process_active_events()
        self.assertEqual(len(expired), 1)

        # Should now be inactive
        active = self.manager.get_active_events()
        self.assertEqual(len(active), 0)

    def test_event_impacts(self):
        """Test event impact calculation."""
        # Trigger multiple events
        event1 = self.manager.event_definitions['market_crash']
        event2 = self.manager.event_definitions['tech_breakthrough']

        self.manager.trigger_event(event1, 1)
        self.manager.trigger_event(event2, 1)

        impacts = self.manager.get_active_event_impacts()

        # Market crash: revenue -0.3, market_share -0.1
        # Tech breakthrough: efficiency +0.2, costs -0.1
        expected_impacts = {
            'revenue': -0.3,
            'market_share': -0.1,
            'efficiency': 0.2,
            'costs': -0.1
        }

        for metric, expected_impact in expected_impacts.items():
            self.assertAlmostEqual(impacts[metric], expected_impact, places=5)

    def test_reset(self):
        """Test event manager reset."""
        self.manager.trigger_event(self.manager.event_definitions['market_crash'], 1)
        self.assertEqual(len(self.manager.get_active_events()), 1)

        self.manager.reset()
        self.assertEqual(len(self.manager.get_active_events()), 0)
        self.assertEqual(len(self.manager.get_event_history()), 0)


if __name__ == '__main__':
    unittest.main()