# Use Case Simulator User Guide

## Overview

The Use Case Simulator is a comprehensive business simulation game that teaches strategic decision-making through hands-on company management. Players make decisions across multiple business functions while competing in dynamic market environments.

## Game Components

### Core Systems

#### 1. Company Management
- **Financial Management**: Revenue, costs, profit, cash flow tracking
- **Operations Management**: Capacity, efficiency, quality control
- **Resource Management**: Employees, equipment, inventory
- **Marketing & Sales**: Brand value, market share, customer acquisition

#### 2. Market Dynamics
- **Demand Simulation**: Price elasticity, economic indicators, seasonal trends
- **Competitive Intelligence**: AI-driven competitor behavior
- **Event System**: Random and scheduled market events
- **Economic Factors**: GDP growth, inflation, interest rates

#### 3. Analytics & Reporting
- **KPI Dashboard**: 15+ key performance indicators
- **Trend Analysis**: Historical performance tracking
- **Custom Reports**: Financial, operational, market reports
- **Visual Charts**: Performance visualization

#### 4. Scenario System
- **Multiple Scenarios**: 4 pre-built scenarios with different challenges
- **Custom Scenarios**: Create and share custom market conditions
- **Difficulty Levels**: Beginner to advanced scenarios
- **Dynamic Switching**: Change scenarios during gameplay

### Technical Architecture

```
Use Case Simulator
├── Core Engine
│   ├── Simulation Engine (main game loop)
│   ├── Round Manager (turn progression)
│   ├── Event Manager (random/scheduled events)
│   ├── State Manager (game state)
│   ├── Company Model (business entity)
│   └── Market Model (economic environment)
├── Analytics System
│   ├── KPI Calculator (performance metrics)
│   ├── Ranking System (competitive analysis)
│   ├── Report Generator (data export)
│   ├── Chart Generator (visualization)
│   └── Leaderboard (achievements)
├── Persistence Layer
│   ├── Data Serializer (save/load system)
│   ├── Company Persistence (entity storage)
│   ├── Market Persistence (scenario storage)
│   └── Simulation Persistence (game saves)
├── Scenario Management
│   ├── Scenario Loader (scenario files)
│   ├── Scenario Manager (runtime switching)
│   └── Template System (pre-built scenarios)
└── User Interface
    └── Console UI (text-based interface)
```

## Installation & Setup

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB for game files + saves
- **OS**: Windows, macOS, Linux

### Installation Methods

#### Method 1: pip Install (Recommended)
```bash
pip install usecasesimulator
```

#### Method 2: From Source
```bash
git clone https://github.com/ShadSafa/UseCaseSimulator.git
cd UseCaseSimulator
pip install -e .
```

### First Run Setup

1. Launch the game:
   ```bash
   python -m modules.ui.console_ui
   ```

2. Choose a company name
3. Select difficulty level
4. Pick a starting scenario
5. Begin playing!

## Gameplay Mechanics

### Game Flow

```
Start Game → Initialize Scenario → Round Loop:
    Display State → Player Decisions → Process Round →
    Update Analytics → Check Win/Loss → Next Round
→ End Game → Final Report
```

### Decision Types

#### Financial Decisions
- **Pricing Strategy**: Set product/service prices
- **Investment Allocation**: Budget for improvements
- **Cost Management**: Control operational expenses

#### Operational Decisions
- **Capacity Planning**: Expand or contract production
- **Quality Control**: Invest in product/service improvements
- **Resource Allocation**: Hire/fire employees, purchase equipment

#### Marketing Decisions
- **Advertising Budget**: Allocate funds for brand building
- **Market Research**: Gather competitor intelligence
- **Customer Focus**: Target specific customer segments

### Performance Metrics

#### Primary KPIs
- **Revenue Growth**: Year-over-year sales increase
- **Profit Margin**: Net profit as percentage of revenue
- **Market Share**: Percentage of total market captured
- **Customer Satisfaction**: Customer loyalty and retention

#### Secondary KPIs
- **Cash Flow**: Net cash position and liquidity
- **Asset Turnover**: Efficiency of asset utilization
- **Employee Productivity**: Revenue per employee
- **Quality Index**: Product/service quality score

### Market Events

#### Random Events
- **Economic Shocks**: Recessions, booms, inflation changes
- **Competitor Actions**: Price wars, new product launches
- **Supply Chain Issues**: Cost increases, delivery delays
- **Regulatory Changes**: New laws affecting business

#### Scheduled Events
- **Seasonal Trends**: Holiday shopping spikes, summer slowdowns
- **Industry Conferences**: Networking opportunities
- **Technology Releases**: New tools becoming available
- **Market Milestones**: Industry anniversaries

## Advanced Features

### Scenario System

#### Pre-built Scenarios

##### 1. Booming Economy (Easy)
- High demand growth
- Favorable economic conditions
- Focus: Scaling operations, managing growth

##### 2. Economic Recession (Hard)
- Reduced demand
- High competition
- Focus: Cost control, survival strategies

##### 3. Technology Disruption (Medium)
- Rapid innovation required
- Quality expectations increasing
- Focus: R&D investment, adaptation

##### 4. Global Expansion (Medium)
- International market dynamics
- Currency fluctuations
- Focus: Diversification, risk management

#### Custom Scenario Creation

```json
{
  "title": "My Custom Scenario",
  "description": "A unique market challenge",
  "difficulty": "medium",
  "market_conditions": {
    "demand_level": 1200.0,
    "competition_intensity": 0.6
  },
  "starting_conditions": {
    "company": { /* custom starting company */ },
    "competitors": [ /* custom competitors */ ]
  }
}
```

### Analytics Deep Dive

#### KPI Categories

##### Financial Analytics
```
Profit & Loss Statement
├── Revenue Streams
├── Cost Breakdown
├── Margin Analysis
└── Cash Flow Statement
```

##### Operational Analytics
```
Efficiency Metrics
├── Capacity Utilization
├── Production Efficiency
├── Quality Control
└── Resource Optimization
```

##### Market Analytics
```
Competitive Intelligence
├── Market Share Trends
├── Competitor Benchmarking
├── Brand Value Tracking
└── Customer Segmentation
```

#### Report Types

- **Summary Reports**: High-level performance overview
- **Detailed Reports**: Drill-down into specific metrics
- **Trend Reports**: Historical performance analysis
- **Comparative Reports**: Peer group analysis

### Save/Load System

#### Save Types

##### 1. Quick Save
- Instant save to default slot
- Overwrites previous quick save
- Fast access during gameplay

##### 2. Manual Save
- Named save files
- Multiple save slots
- Includes save descriptions

##### 3. Auto Save
- Automatic saves every N rounds
- Configurable frequency
- Backup protection

##### 4. Scenario Saves
- Save current state as new scenario
- Shareable with other players
- Template for similar games

#### Save File Structure

```
data/saves/
├── quicksave.json
├── manual_saves/
│   ├── game_session_1.json
│   └── game_session_2.json
├── auto_saves/
│   ├── autosave_round_5.json
│   ├── autosave_round_10.json
│   └── autosave_round_15.json
└── scenario_saves/
    └── my_custom_scenario.json
```

### Leaderboards & Achievements

#### Achievement System

##### Financial Achievements
- **Profit Master**: Reach 25% profit margin
- **Cash Flow King**: 5+ rounds of positive cash flow
- **ROI Champion**: Return on investment > 30%

##### Operational Achievements
- **Efficiency Expert**: Operational efficiency > 90%
- **Quality Guru**: Quality index > 95%
- **Capacity Master**: 95%+ capacity utilization

##### Market Achievements
- **Market Leader**: Top market share position
- **Brand Builder**: Brand value > 100
- **Customer Champion**: Satisfaction > 90%

#### Leaderboard Categories

- **Overall Performance**: Combined score across all KPIs
- **Financial Excellence**: Pure financial performance
- **Operational Mastery**: Operations and efficiency focus
- **Market Dominance**: Market share and positioning
- **Customer Focus**: Customer satisfaction metrics

## Configuration

### Game Settings

#### Difficulty Levels
```python
# In simulation_config.py
SimulationConfig(
    max_rounds=15,           # Game length
    num_competitors=4,       # AI competitors
    initial_market_demand=1000.0,
    market_volatility=0.2,   # Economic stability
    event_frequency=0.3      # Event occurrence rate
)
```

#### Analytics Settings
```python
# In analytics_config.py
AnalyticsConfig(
    auto_generate_reports=True,
    auto_generate_charts=True,
    kpi_update_frequency=1,    # Rounds between updates
    chart_resolution='high'
)
```

### Custom Scenarios

#### Scenario File Format
```json
{
  "title": "Custom Scenario",
  "description": "Your scenario description",
  "difficulty": "medium",
  "estimated_duration": 12,
  "tags": ["custom", "challenging"],
  "version": "1.0",
  "created_at": "2025-01-01T00:00:00",

  "market_conditions": {
    "demand_level": 1000.0,
    "price_index": 1.0,
    "competition_intensity": 0.5,
    "economic_indicators": {
      "gdp_growth": 0.02,
      "inflation": 0.03,
      "interest_rate": 0.05
    }
  },

  "starting_conditions": {
    "company": { /* company data */ },
    "competitors": [ /* competitor data */ ],
    "round_number": 0
  },

  "simulation_config": {
    "max_rounds": 12,
    "num_competitors": 3,
    "initial_market_demand": 1000.0,
    "market_volatility": 0.15,
    "event_frequency": 0.25
  }
}
```

## Troubleshooting

### Common Issues

#### Performance Problems
**Symptoms**: Slow loading, lag during gameplay
**Solutions**:
- Reduce chart generation frequency
- Disable auto-analytics
- Close other applications
- Upgrade to faster storage

#### Save File Corruption
**Symptoms**: "Invalid save file" errors
**Solutions**:
- Use backup saves
- Validate JSON syntax
- Start new game
- Check file permissions

#### Memory Issues
**Symptoms**: Out of memory errors
**Solutions**:
- Reduce simulation history length
- Disable detailed analytics
- Close other programs
- Increase system RAM

### Debug Mode

Enable debug logging:
```bash
export SIMULATOR_DEBUG=1
python -m modules.ui.console_ui
```

### Getting Help

1. **In-game Help**: Press 'H' in any menu
2. **Documentation**: Check docs/ folder
3. **GitHub Issues**: Report bugs with save files
4. **Community**: Join discussions for tips

## Development

### Architecture Overview

The simulator follows a modular architecture:

- **Separation of Concerns**: Each module handles specific functionality
- **Dependency Injection**: Loose coupling between components
- **Event-Driven Design**: Reactive system updates
- **Data Persistence**: Robust save/load system

### Extending the Game

#### Adding New KPIs
```python
# In kpi_calculator.py
def calculate_custom_kpi(self, company_data, market_data):
    return company_data['revenue'] / company_data['employees']
```

#### Creating New Scenarios
```python
# Use the scenario template system
scenario_manager.create_scenario_from_template(
    "boom_economy",
    "my_boom_scenario",
    {"market_conditions.demand_level": 2000.0}
)
```

#### Custom Events
```python
# In event_manager.py
custom_event = Event(
    id="custom_event",
    name="Special Market Event",
    impacts={"demand_change": 0.1},
    duration=3
)
```

## API Reference

### Core Classes

#### SimulationEngine
```python
engine = SimulationEngine(config)
engine.initialize_simulation()
results = engine.run_round(decisions)
engine.save_simulation("save_name")
```

#### AnalyticsManager
```python
analytics = AnalyticsManager()
kpis = analytics.calculate_kpis(company_data, market_data)
report = analytics.generate_report(simulation_data)
```

#### ScenarioManager
```python
scenarios = ScenarioManager()
scenario_data = scenarios.load_scenario("scenario_name")
scenarios.apply_scenario_to_simulation("scenario_name", engine)
```

## Changelog

### Version 1.0.0
- Initial release
- Core simulation engine
- Basic analytics and reporting
- Scenario system
- Save/load functionality
- Console user interface

### Future Versions
- Web-based UI
- Multiplayer support
- Advanced AI competitors
- Mobile app
- Cloud saves

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Documentation**: docs/ folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@usecasesimulator.com

---

*Use Case Simulator - Learn business strategy through interactive simulation*