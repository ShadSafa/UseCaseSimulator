import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
from pathlib import Path


class ChartGenerator:
    """Generates various charts for simulation analytics."""

    def __init__(self, output_dir: str = "data/charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set matplotlib style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10

    def generate_kpi_trend_chart(self, kpi_data: List[Dict[str, Any]],
                                kpi_name: str, company_name: str = "Company") -> str:
        """Generate a KPI trend chart over time.

        Args:
            kpi_data: List of KPI data points with timestamps
            kpi_name: Name of the KPI to chart
            company_name: Name of the company

        Returns:
            Path to generated chart file
        """
        if not kpi_data:
            return ""

        # Extract data
        rounds = []
        values = []
        timestamps = []

        for i, data_point in enumerate(kpi_data):
            rounds.append(i + 1)
            value = self._extract_kpi_value(data_point, kpi_name)
            values.append(value)
            timestamps.append(data_point.get('timestamp', datetime.now()))

        # Create chart
        fig, ax = plt.subplots()

        ax.plot(rounds, values, marker='o', linewidth=2, markersize=6, color='#2E86AB')

        # Formatting
        ax.set_title(f'{kpi_name.replace("_", " ").title()} Trend - {company_name}')
        ax.set_xlabel('Round')
        ax.set_ylabel(kpi_name.replace("_", " ").title())
        ax.grid(True, alpha=0.3)

        # Add value labels on points
        for i, value in enumerate(values):
            ax.annotate(f'{value:.2f}', (rounds[i], values[i]),
                       xytext=(0, 10), textcoords='offset points',
                       ha='center', fontsize=8)

        plt.tight_layout()

        # Save chart
        filename = f"kpi_trend_{kpi_name}_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_multi_kpi_chart(self, kpi_data: List[Dict[str, Any]],
                                kpi_names: List[str], company_name: str = "Company") -> str:
        """Generate a chart with multiple KPIs.

        Args:
            kpi_data: List of KPI data points
            kpi_names: List of KPI names to include
            company_name: Name of the company

        Returns:
            Path to generated chart file
        """
        if not kpi_data or not kpi_names:
            return ""

        rounds = list(range(1, len(kpi_data) + 1))

        fig, ax = plt.subplots()

        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B4D61']
        for i, kpi_name in enumerate(kpi_names):
            values = [self._extract_kpi_value(data_point, kpi_name) for data_point in kpi_data]
            color = colors[i % len(colors)]
            ax.plot(rounds, values, marker='o', label=kpi_name.replace("_", " ").title(),
                   linewidth=2, markersize=4, color=color)

        ax.set_title(f'Multiple KPIs Trend - {company_name}')
        ax.set_xlabel('Round')
        ax.set_ylabel('KPI Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        filename = f"multi_kpi_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_ranking_bar_chart(self, rankings: List[Dict[str, Any]],
                                  category: str = "overall") -> str:
        """Generate a bar chart of company rankings.

        Args:
            rankings: List of ranking data
            category: Ranking category

        Returns:
            Path to generated chart file
        """
        if not rankings:
            return ""

        # Take top 10 for readability
        top_rankings = rankings[:10]

        companies = [r.get('company_name', f'Company {r["rank"]}') for r in top_rankings]
        scores = [r['score'] for r in top_rankings]

        fig, ax = plt.subplots()

        bars = ax.barh(range(len(companies)), scores, color='#2E86AB', alpha=0.8)

        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + max(scores) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{scores[i]:.1f}', ha='left', va='center', fontweight='bold')

        ax.set_yticks(range(len(companies)))
        ax.set_yticklabels(companies)
        ax.set_xlabel('Score')
        ax.set_title(f'Top 10 Companies - {category.replace("_", " ").title()} Ranking')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        filename = f"ranking_bar_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_market_share_pie_chart(self, market_data: List[Dict[str, Any]]) -> str:
        """Generate a pie chart of market share distribution.

        Args:
            market_data: List of company market data

        Returns:
            Path to generated chart file
        """
        if not market_data:
            return ""

        # Extract market shares
        labels = []
        sizes = []

        for company in market_data:
            market_share = company.get('market_share', 0) * 100  # Convert to percentage
            if market_share > 1:  # Only show companies with >1% share
                company_name = company.get('company_name', company.get('name', f'Company {company["id"]}'))
                labels.append(company_name)
                sizes.append(market_share)

        # Group small shares into "Others"
        if len(sizes) > 8:
            # Sort by size descending
            combined = sorted(zip(sizes, labels), reverse=True)
            sizes, labels = zip(*combined)

            # Keep top 7, sum the rest
            top_sizes = list(sizes[:7])
            top_labels = list(labels[:7])
            other_size = sum(sizes[7:])

            if other_size > 0:
                top_sizes.append(other_size)
                top_labels.append('Others')

            sizes = top_sizes
            labels = top_labels

        fig, ax = plt.subplots()

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         startangle=90, colors=plt.cm.Set3.colors)

        ax.set_title('Market Share Distribution')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

        # Improve text readability
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)

        plt.tight_layout()

        filename = f"market_share_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_financial_statement_chart(self, financial_data: List[Dict[str, Any]],
                                         company_name: str = "Company") -> str:
        """Generate a financial statement visualization.

        Args:
            financial_data: List of financial data points over time
            company_name: Name of the company

        Returns:
            Path to generated chart file
        """
        if not financial_data:
            return ""

        rounds = list(range(1, len(financial_data) + 1))

        # Extract financial metrics
        revenue = [d.get('revenue', 0) for d in financial_data]
        costs = [d.get('costs', 0) for d in financial_data]
        profit = [d.get('profit', 0) for d in financial_data]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Revenue and costs
        ax1.plot(rounds, revenue, marker='o', label='Revenue', color='#2E86AB', linewidth=2)
        ax1.plot(rounds, costs, marker='s', label='Costs', color='#A23B72', linewidth=2)
        ax1.fill_between(rounds, costs, revenue, where=(np.array(revenue) >= np.array(costs)),
                        alpha=0.3, color='#2E86AB', label='Profit Area')
        ax1.set_title(f'Financial Performance - {company_name}')
        ax1.set_ylabel('Amount ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Profit trend
        colors = ['green' if p >= 0 else 'red' for p in profit]
        ax2.bar(rounds, profit, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Profit/Loss Trend')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Profit ($)')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        filename = f"financial_statement_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_performance_radar_chart(self, kpi_data: Dict[str, float],
                                        company_name: str = "Company") -> str:
        """Generate a radar chart of company performance across KPIs.

        Args:
            kpi_data: Dictionary of KPI values
            company_name: Name of the company

        Returns:
            Path to generated chart file
        """
        if not kpi_data:
            return ""

        # Select key KPIs for radar chart
        key_kpis = ['profit_margin', 'market_share', 'customer_satisfaction',
                   'operational_efficiency', 'capacity_utilization']

        # Extract values (scale to 0-100 for radar)
        labels = []
        values = []

        for kpi in key_kpis:
            if kpi in kpi_data:
                labels.append(kpi.replace("_", " ").title())
                value = kpi_data[kpi]
                # Scale different KPIs appropriately
                if kpi in ['profit_margin', 'operational_efficiency', 'capacity_utilization', 'customer_satisfaction']:
                    scaled_value = min(100, max(0, value * 100))
                elif kpi == 'market_share':
                    scaled_value = min(100, max(0, value * 100))
                else:
                    scaled_value = min(100, max(0, value))
                values.append(scaled_value)

        if len(values) < 3:  # Need at least 3 points for radar
            return ""

        # Close the polygon
        values += values[:1]
        labels += labels[:1]

        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        ax.plot(angles, values, 'o-', linewidth=2, label=company_name, color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels[:-1])
        ax.set_ylim(0, 100)
        ax.set_title(f'Performance Radar - {company_name}', size=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)

        # Add value labels
        for angle, value, label in zip(angles[:-1], values[:-1], labels[:-1]):
            ax.text(angle, value + 5, f'{value:.1f}', ha='center', va='center', fontweight='bold')

        plt.tight_layout()

        filename = f"performance_radar_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def generate_comparison_chart(self, companies_data: List[Dict[str, Any]],
                                 kpi_name: str) -> str:
        """Generate a comparison chart across companies for a specific KPI.

        Args:
            companies_data: List of company data
            kpi_name: KPI to compare

        Returns:
            Path to generated chart file
        """
        if not companies_data:
            return ""

        companies = []
        values = []

        for company in companies_data:
            company_name = company.get('company_name', company.get('name', f'Company {company["id"]}'))
            value = self._extract_kpi_value(company, kpi_name)

            if value is not None:
                companies.append(company_name)
                values.append(value)

        if not values:
            return ""

        fig, ax = plt.subplots()

        bars = ax.bar(range(len(companies)), values, color='#2E86AB', alpha=0.8)

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                   f'{value:.2f}', ha='center', va='bottom', fontweight='bold')

        ax.set_xticks(range(len(companies)))
        ax.set_xticklabels(companies, rotation=45, ha='right')
        ax.set_ylabel(kpi_name.replace("_", " ").title())
        ax.set_title(f'{kpi_name.replace("_", " ").title()} Comparison Across Companies')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        filename = f"comparison_{kpi_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)

    def _extract_kpi_value(self, data_point: Dict[str, Any], kpi_name: str) -> Optional[float]:
        """Extract KPI value from data point."""
        # Try different possible locations for KPI data
        if 'kpis' in data_point and kpi_name in data_point['kpis']:
            return data_point['kpis'][kpi_name]

        # Try direct access
        if kpi_name in data_point:
            return data_point[kpi_name]

        # Try nested in financial/operational data
        for category in ['financial_data', 'operations_data', 'market_data']:
            if category in data_point and kpi_name in data_point[category]:
                return data_point[category][kpi_name]

        return None

    def generate_dashboard_charts(self, simulation_data: Dict[str, Any],
                                company_name: str = "Company") -> List[str]:
        """Generate a set of dashboard charts.

        Args:
            simulation_data: Complete simulation data
            company_name: Name of the company

        Returns:
            List of generated chart file paths
        """
        chart_files = []

        # Extract historical data
        historical_data = simulation_data.get('historical_data', [])

        if historical_data:
            # KPI trends
            key_kpis = ['profit_margin', 'market_share', 'customer_satisfaction', 'operational_efficiency']
            for kpi in key_kpis:
                chart_file = self.generate_kpi_trend_chart(historical_data, kpi, company_name)
                if chart_file:
                    chart_files.append(chart_file)

            # Multi-KPI chart
            chart_file = self.generate_multi_kpi_chart(historical_data, key_kpis[:4], company_name)
            if chart_file:
                chart_files.append(chart_file)

            # Financial statement chart
            financial_history = []
            for data_point in historical_data:
                if 'financial_data' in data_point:
                    financial_history.append(data_point['financial_data'])
            if financial_history:
                chart_file = self.generate_financial_statement_chart(financial_history, company_name)
                if chart_file:
                    chart_files.append(chart_file)

        # Current KPIs radar chart
        current_kpis = simulation_data.get('current_kpis', {})
        if current_kpis:
            chart_file = self.generate_performance_radar_chart(current_kpis, company_name)
            if chart_file:
                chart_files.append(chart_file)

        return chart_files