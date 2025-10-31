"""
Console-based User Interface for UseCaseSimulator
Provides text-based interface for business simulation.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.simulation_engine import SimulationEngine, SimulationConfig
from ..core.simulation_state import SimulationState


class ConsoleUI:
    """Main console UI class for the business simulation."""

    def __init__(self):
        self.engine: Optional[SimulationEngine] = None
        self.current_state: Optional[SimulationState] = None
        self.running = False

    def start(self):
        """Start the console UI application."""
        self.running = True
        self._clear_screen()
        self._show_welcome()
        self._main_menu()

    def stop(self):
        """Stop the console UI application."""
        self.running = False
        print("\nThank you for using UseCaseSimulator!")
        sys.exit(0)

    def _clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _show_welcome(self):
        """Display welcome message."""
        print("=" * 60)
        print("           WELCOME TO USECASE SIMULATOR")
        print("=" * 60)
        print("A business simulation where you make strategic")
        print("decisions to grow your company and compete in the market.")
        print("=" * 60)
        print()

    def _main_menu(self):
        """Display and handle main menu."""
        while self.running:
            print("\nMAIN MENU")
            print("-" * 30)
            print("1. New Simulation")
            print("2. Load Simulation")
            print("3. Help")
            print("4. Exit")
            print()

            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                self._start_new_simulation()
            elif choice == "2":
                self._load_simulation()
            elif choice == "3":
                self._show_help()
            elif choice == "4":
                self.stop()
            else:
                print("Invalid choice. Please try again.")

    def _start_new_simulation(self):
        """Initialize and start a new simulation."""
        self._clear_screen()
        print("STARTING NEW SIMULATION")
        print("-" * 30)

        # Create simulation engine
        config = SimulationConfig()
        self.engine = SimulationEngine(config)

        # Initialize simulation
        try:
            self.current_state = self.engine.initialize_simulation()
            print("Simulation initialized successfully!")
            print(f"Welcome, {self.current_state.player_company.name}!")
            input("\nPress Enter to continue...")
            self._simulation_loop()
        except Exception as e:
            print(f"Error initializing simulation: {e}")
            input("Press Enter to return to main menu...")

    def _load_simulation(self):
        """Load a saved simulation."""
        self._clear_screen()
        print("LOAD SIMULATION")
        print("-" * 30)

        # List available saves
        saves_dir = "data/saves"
        if not os.path.exists(saves_dir):
            print("No saved games found.")
            input("Press Enter to return to main menu...")
            return

        saves = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        if not saves:
            print("No saved simulations found.")
            input("Press Enter to return to main menu...")
            return

        print("Available saves:")
        for i, save in enumerate(saves, 1):
            save_name = save.replace('.json', '')
            print(f"{i}. {save_name}")

        print("0. Cancel")
        print()

        try:
            choice = int(input("Select save to load (0 to cancel): ").strip())
            if choice == 0:
                return
            if 1 <= choice <= len(saves):
                save_file = saves[choice - 1].replace('.json', '')
                self._load_simulation_file(save_file)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        input("Press Enter to continue...")

    def _load_simulation_file(self, filename: str):
        """Load a specific simulation file."""
        try:
            config = SimulationConfig()
            self.engine = SimulationEngine(config)
            self.current_state = self.engine.load_simulation(filename)
            if self.current_state:
                print(f"Simulation loaded successfully! Round {self.current_state.round_number}")
                input("Press Enter to continue...")
                self._simulation_loop()
            else:
                print("Failed to load simulation.")
        except Exception as e:
            print(f"Error loading simulation: {e}")

    def _show_help(self):
        """Display help information."""
        self._clear_screen()
        print("HELP - UseCase Simulator")
        print("=" * 40)
        print("OVERVIEW:")
        print("UseCase Simulator is a business simulation where you")
        print("manage a company and make strategic decisions to compete")
        print("in the market.")
        print()
        print("GAMEPLAY:")
        print("- Each round represents a business quarter")
        print("- Make decisions about pricing, investments, marketing")
        print("- Monitor your company's performance and market conditions")
        print("- Compete against AI-controlled competitors")
        print("- Events can occur that affect the market")
        print()
        print("DECISIONS:")
        print("- Pricing: Set product prices")
        print("- Marketing: Allocate budget for marketing campaigns")
        print("- Investment: Invest in capacity expansion or quality improvement")
        print("- Hiring: Hire additional employees")
        print("- Equipment: Purchase new equipment")
        print()
        print("KEY METRICS:")
        print("- Revenue: Total sales income")
        print("- Profit: Revenue minus costs")
        print("- Market Share: Percentage of market controlled")
        print("- Customer Satisfaction: How happy customers are")
        print("- Efficiency: Operational efficiency")
        print()

        input("Press Enter to return to main menu...")

    def _simulation_loop(self):
        """Main simulation loop for playing rounds."""
        while self.running and self.current_state and not self.engine.round_manager.is_game_over():
            self._clear_screen()
            self._show_dashboard()

            # Check if simulation is over
            if self.engine.round_manager.is_simulation_over():
                self._show_simulation_over()
                break

            # Get player decisions
            decisions = self._get_player_decisions()

            if decisions is None:  # Player chose to save/exit
                break

            # Run the round
            try:
                round_results = self.engine.run_round(decisions)
                self.current_state = SimulationState.from_dict(round_results['game_state'])

                # Show round summary
                self._show_round_summary(round_results)

                # Continue to next round
                input("\nPress Enter to continue to next round...")

            except Exception as e:
                print(f"Error running round: {e}")
                input("Press Enter to continue...")

        # Simulation over or exited
        if self.engine and self.engine.round_manager.is_simulation_over():
            self._show_simulation_over()

    def _show_dashboard(self):
        """Display the company dashboard."""
        if not self.current_state:
            return

        company = self.current_state.player_company
        market = self.current_state.market

        print("=" * 60)
        print(f"COMPANY DASHBOARD - Round {self.current_state.round_number}")
        print("=" * 60)

        # Company Overview
        print(f"Company: {company.name}")
        print(f"Round: {self.current_state.round_number}")
        print()

        # Financial Status
        print("FINANCIAL STATUS")
        print("-" * 20)
        print(".2f")
        print(".2f")
        print(".2f")
        print(".2f")
        print()

        # Operational Status
        print("OPERATIONAL STATUS")
        print("-" * 20)
        print(".1f")
        print(".1%")
        print(".1%")
        print(".1%")
        print()

        # Market Position
        print("MARKET POSITION")
        print("-" * 20)
        print(".1%")
        print(".0f")
        print(".1f")
        print()

        # Market Conditions
        market_summary = market.get_market_summary()
        print("MARKET CONDITIONS")
        print("-" * 20)
        print(".0f")
        print(".2f")
        print(".1%")
        print(f"Active Events: {len(market_summary.get('active_events', []))}")
        print()

        # Competitors
        competitors = market_summary.get('competitors', [])
        if competitors:
            print("TOP COMPETITORS")
            print("-" * 20)
            for comp in competitors[:3]:  # Show top 3
                print(".1%")
            print()

    def _get_player_decisions(self) -> Optional[Dict[str, Any]]:
        """Get player decisions for the current round."""
        decisions = {}

        print("DECISION PHASE")
        print("-" * 20)
        print("Make your business decisions for this round:")
        print()

        # Pricing Decision
        print("1. PRICING DECISION")
        try:
            current_price = 100.0  # Default price
            price_input = input(f"Enter product price (current: ${current_price:.2f}, press Enter for no change): ").strip()
            if price_input:
                price = float(price_input)
                if 10 <= price <= 500:  # Reasonable price range
                    decisions['pricing'] = {'price': price}
                else:
                    print("Price must be between $10 and $500. Using current price.")
        except ValueError:
            print("Invalid price. Using current price.")

        # Marketing Budget
        print("\n2. MARKETING BUDGET")
        try:
            budget_input = input("Enter marketing budget ($0 for none): ").strip()
            if budget_input:
                budget = float(budget_input)
                if budget >= 0:
                    decisions['marketing'] = {'budget': budget}
                else:
                    print("Budget cannot be negative.")
        except ValueError:
            print("Invalid budget amount.")

        # Investment Decision
        print("\n3. INVESTMENT DECISION")
        print("Choose investment type:")
        print("1. Capacity Expansion")
        print("2. Quality Improvement")
        print("3. No Investment")
        try:
            inv_choice = input("Enter choice (1-3): ").strip()
            if inv_choice == "1":
                amount = float(input("Enter expansion amount: ").strip())
                if amount > 0:
                    decisions['capacity_expansion'] = {'expansion_amount': amount}
            elif inv_choice == "2":
                investment = float(input("Enter quality investment amount: ").strip())
                if investment > 0:
                    decisions['quality_improvement'] = {'investment': investment}
        except ValueError:
            print("Invalid input.")

        # Hiring Decision
        print("\n4. HIRING DECISION")
        try:
            hire_input = input("Enter number of employees to hire (0 for none): ").strip()
            if hire_input:
                num_employees = int(hire_input)
                if num_employees > 0:
                    decisions['hiring'] = {'num_employees': num_employees}
        except ValueError:
            print("Invalid number.")

        # Equipment Purchase
        print("\n5. EQUIPMENT PURCHASE")
        try:
            equip_input = input("Enter equipment purchase amount ($0 for none): ").strip()
            if equip_input:
                equip_value = float(equip_input)
                if equip_value > 0:
                    decisions['equipment_purchase'] = {'equipment_value': equip_value}
        except ValueError:
            print("Invalid amount.")

        # Menu options
        print("\nOPTIONS:")
        print("R. Review decisions")
        print("S. Save simulation")
        print("Q. Quit to main menu")
        print("C. Continue with decisions")

        while True:
            option = input("\nEnter option (R/S/Q/C): ").strip().upper()
            if option == "R":
                self._review_decisions(decisions)
            elif option == "S":
                self._save_simulation_prompt()
            elif option == "Q":
                return None
            elif option == "C":
                return decisions
            else:
                print("Invalid option.")

    def _review_decisions(self, decisions: Dict[str, Any]):
        """Review current decisions."""
        print("\nDECISION REVIEW")
        print("-" * 20)
        if not decisions:
            print("No decisions made.")
        else:
            for decision_type, params in decisions.items():
                print(f"{decision_type.upper()}: {params}")
        print()

    def _save_simulation_prompt(self):
        """Prompt to save the current simulation."""
        save_name = input("Enter save name (or press Enter to cancel): ").strip()
        if save_name and self.engine:
            if self.engine.save_simulation(save_name):
                print("Simulation saved successfully!")
            else:
                print("Failed to save simulation.")
        input("Press Enter to continue...")

    def _show_round_summary(self, round_results: Dict[str, Any]):
        """Display round summary and results."""
        self._clear_screen()
        print("=" * 60)
        print(f"ROUND {round_results['round_number']} SUMMARY")
        print("=" * 60)

        round_data = round_results.get('round_results', {})

        # Financial Results
        print("FINANCIAL RESULTS")
        print("-" * 20)
        print(".2f")
        print(".2f")
        print(".2f")
        print()

        # Market Results
        print("MARKET RESULTS")
        print("-" * 20)
        print(".1%")
        print(".1%")
        print()

        # Events
        triggered_events = round_results.get('triggered_events', [])
        if triggered_events:
            print("EVENTS THIS ROUND")
            print("-" * 20)
            for event in triggered_events:
                print(f"- {event.get('description', 'Unknown event')}")
            print()

        # Performance Summary
        print("PERFORMANCE SUMMARY")
        print("-" * 20)
        if round_data.get('profit', 0) > 0:
            print("✓ Profitable round")
        else:
            print("✗ Loss-making round")

        if round_data.get('market_share', 0) > 0.15:  # Assuming 15% is baseline
            print("✓ Gaining market share")
        elif round_data.get('market_share', 0) < 0.15:
            print("✗ Losing market share")
        else:
            print("→ Market share stable")

        print()

    def _show_simulation_over(self):
        """Display simulation over screen."""
        self._clear_screen()
        print("=" * 60)
        print("SIMULATION OVER")
        print("=" * 60)

        if self.current_state:
            company = self.current_state.player_company
            print(f"Final Round: {self.current_state.round_number}")
            print(f"Company: {company.name}")
            print()
            print("FINAL FINANCIAL POSITION")
            print("-" * 30)
            print(".2f")
            print(".2f")
            print(".2f")
            print()
            print("FINAL MARKET POSITION")
            print("-" * 30)
            print(".1%")
            print(".1%")
            print()

            # Simple performance rating
            profit = company.financial_data.profit
            market_share = company.market_data.market_share

            if profit > 50000 and market_share > 0.25:
                rating = "EXCELLENT - Outstanding performance!"
            elif profit > 20000 and market_share > 0.15:
                rating = "GOOD - Solid business results"
            elif profit > 0:
                rating = "FAIR - Breaking even"
            else:
                rating = "POOR - Significant losses"

            print(f"PERFORMANCE RATING: {rating}")

        print("\nThank you for using UseCaseSimulator!")
        input("\nPress Enter to return to main menu...")

        # Reset simulation state
        self.current_state = None
        self.engine = None