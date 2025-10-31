#!/usr/bin/env python3
"""
Console-based runner for the Use Case Simulator.
Provides a command-line interface for running simulations without the web UI.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from modules.core.simulation_engine import SimulationEngine, SimulationConfig
from modules.analytics.analytics_manager import AnalyticsManager


def run_console_simulation():
    """Run a console-based simulation."""
    print("Use Case Simulator - Console Mode")
    print("=" * 50)

    # Create simulation configuration
    config = SimulationConfig(
        max_rounds=5,  # Short simulation for testing
        num_competitors=2,
        initial_market_demand=1000.0
    )

    # Initialize simulation engine
    engine = SimulationEngine(config)
    analytics = AnalyticsManager()

    try:
        # Initialize simulation
        print("\nInitializing simulation...")
        state = engine.initialize_simulation()
        print(f"Simulation initialized with {len(state.competitors)} competitors")

        # Display initial state
        print(f"\nInitial Company State:")
        print(f"   Revenue: ${state.player_company.financial_data.revenue:,.0f}")
        print(f"   Market Share: {state.player_company.market_data.market_share:.1%}")
        print(f"   Cash: ${state.player_company.financial_data.cash:,.0f}")

        # Run simulation rounds
        for round_num in range(1, config.max_rounds + 1):
            print(f"\nRound {round_num}")
            print("-" * 20)

            # Make some basic decisions (could be made interactive)
            decisions = {
                'price_change': {'new_price': 95.0 + round_num},  # Gradual price increase
                'marketing_campaign': {'budget': 10000 + round_num * 2000}  # Increasing marketing spend
            }

            print(f"   Decisions: Price -> ${decisions['price_change']['new_price']:.0f}, Marketing -> ${decisions['marketing_campaign']['budget']:,}")

            # Run the round
            result = engine.run_round(decisions)

            # Process analytics
            analytics_results = analytics.process_round_analytics(
                [state.player_company.to_dict()],
                {'demand_level': 1000.0, 'price_index': 1.0},
                round_num
            )

            # Display round results
            print(f"   Revenue: ${result['round_results'].get('revenue', 0):,.0f}")
            print(f"   Profit: ${result['round_results'].get('profit', 0):,.0f}")
            print(f"   Market Share: {result['round_results'].get('market_share', 0):.1%}")

            if result['triggered_events']:
                print(f"   Events: {len(result['triggered_events'])} triggered")

        # Final results
        final_state = engine.get_current_state()
        print(f"\nFinal Results:")
        print(f"   Total Rounds: {final_state.round_number}")
        print(f"   Final Revenue: ${final_state.player_company.financial_data.revenue:,.0f}")
        print(f"   Final Profit: ${final_state.player_company.financial_data.profit:,.0f}")
        print(f"   Final Market Share: {final_state.player_company.market_data.market_share:.1%}")
        print(f"   Customer Satisfaction: {final_state.player_company.operations_data.customer_satisfaction:.1%}")

        # Analytics summary
        analytics_summary = analytics.get_analytics_summary()
        print(f"\nAnalytics Summary:")
        print(f"   Rounds Analyzed: {analytics_summary['total_rounds_analyzed']}")
        print(f"   KPIs Calculated: {analytics_summary['kpi_summary']['total_kpis_calculated']}")

        print("\nConsole simulation completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_basic_tests():
    """Run basic functionality tests."""
    print("\nRunning Basic Tests...")
    print("-" * 30)

    try:
        # Test simulation engine
        engine = SimulationEngine()
        state = engine.initialize_simulation()
        print("Simulation engine initialized")

        # Test analytics
        analytics = AnalyticsManager()
        results = analytics.process_round_analytics(
            [state.player_company.to_dict()],
            {'demand_level': 1000.0},
            1
        )
        print("Analytics processing works")

        # Test company operations
        company = state.player_company
        revenue = company.calculate_revenue(1000.0, 100.0)
        print(f"Revenue calculation: ${revenue:,.0f}")

        print("All basic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main console application."""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Run basic tests
        success = run_basic_tests()
    else:
        # Run full simulation
        success = run_console_simulation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()