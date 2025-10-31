# Use Case Simulator Tutorial

Welcome to the Use Case Simulator! This interactive business simulation game teaches strategic decision-making through hands-on experience managing a company in a dynamic market environment.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Game](#understanding-the-game)
3. [Making Decisions](#making-decisions)
4. [Monitoring Performance](#monitoring-performance)
5. [Advanced Features](#advanced-features)
6. [Tips for Success](#tips-for-success)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

1. **Prerequisites**: Python 3.8 or higher
2. **Install the game**:
   ```bash
   pip install usecasesimulator
   ```
3. **Run the game**:
   ```bash
   python -m modules.ui.console_ui
   ```

### First Time Setup

When you start the game for the first time, you'll be prompted to:

1. Choose a company name
2. Select a starting scenario (beginner-friendly options available)
3. Review the basic controls

## Understanding the Game

### Game Objective

Your goal is to successfully manage a business over multiple rounds (typically 10-15 rounds) by making strategic decisions that balance:

- **Financial Performance**: Revenue growth, profitability, cash management
- **Operational Efficiency**: Capacity utilization, quality control, cost management
- **Market Position**: Market share, brand value, competitive positioning
- **Customer Satisfaction**: Service quality, loyalty, retention

### Key Concepts

#### Company Metrics
- **Revenue**: Income from sales
- **Costs**: Operational expenses (fixed + variable)
- **Profit**: Revenue minus costs
- **Cash Flow**: Net cash movement
- **Market Share**: Percentage of market controlled
- **Capacity Utilization**: How efficiently you use production capacity

#### Market Dynamics
- **Demand**: Customer demand for your products/services
- **Competition**: Rival companies vying for market share
- **Economic Conditions**: GDP growth, inflation, interest rates
- **Events**: Random or scheduled events that impact the business

## Making Decisions

### Decision Types

Each round, you can make several types of business decisions:

#### 1. Pricing Decisions
```
Current Price: $100.00
Market Average: $98.00
Recommended Range: $90.00 - $110.00

Enter new price: 105.00
```
**Impact**: Affects demand, revenue, and competitive position.

#### 2. Capacity Expansion
```
Current Capacity: 1000 units
Utilization: 85%
Expansion Cost: $50,000
Additional Capacity: 200 units

Invest in expansion? (y/n): y
```
**Impact**: Increases production capability but adds fixed costs.

#### 3. Marketing Campaigns
```
Budget Options:
1. $10,000 (Small campaign)
2. $25,000 (Medium campaign)
3. $50,000 (Large campaign)

Choose budget level (1-3): 2
```
**Impact**: Improves brand value and market share.

#### 4. Quality Improvements
```
Current Quality: 75%
Improvement Cost: $15,000
Expected Quality Gain: +5%

Invest in quality? (y/n): y
```
**Impact**: Increases customer satisfaction and premium pricing potential.

#### 5. Hiring Decisions
```
Current Employees: 100
Productivity: 85%
Hiring Cost: $50,000/year
Additional Employees: 10

Hire new employees? (y/n): y
```
**Impact**: Increases operational capacity and efficiency.

### Decision-Making Strategy

1. **Assess Current Situation**: Review KPIs and market conditions
2. **Prioritize Actions**: Focus on 2-3 key decisions per round
3. **Balance Trade-offs**: Consider short-term vs. long-term impacts
4. **Monitor Results**: Track how decisions affect performance

## Monitoring Performance

### Key Performance Indicators (KPIs)

The game tracks several KPIs to measure your success:

#### Financial KPIs
- **Profit Margin**: (Revenue - Costs) / Revenue
- **Return on Assets**: Profit / Total Assets
- **Cash Flow Ratio**: Operating Cash Flow / Revenue
- **Current Ratio**: Cash / Liabilities

#### Operational KPIs
- **Capacity Utilization**: Actual Production / Maximum Capacity
- **Operational Efficiency**: Output per unit of input
- **Quality Index**: Product/service quality score
- **Employee Productivity**: Revenue per employee

#### Market KPIs
- **Market Share**: Your portion of total market
- **Brand Value**: Strength of your brand
- **Competitive Position**: Relative standing vs. competitors
- **Customer Satisfaction**: How happy customers are

#### Customer KPIs
- **Satisfaction Score**: Overall customer happiness
- **Loyalty Index**: Customer retention rate
- **Retention Probability**: Likelihood customers stay
- **Recommendation Likelihood**: Word-of-mouth potential

### Performance Dashboard

```
ROUND 5 SUMMARY
═══════════════════════════════════════════════════════════════

FINANCIAL PERFORMANCE
Revenue: $125,000 (+8.7%)
Costs: $98,000 (+2.1%)
Profit: $27,000 (+25.6%)
Cash: $45,000 (+15.4%)

OPERATIONAL METRICS
Capacity Utilization: 87%
Operational Efficiency: 0.83
Quality Index: 0.78
Customer Satisfaction: 0.82

MARKET POSITION
Market Share: 16.5% (+1.2%)
Brand Value: 52.0 (+4.0%)
Competitive Position: 0.55 (+0.05)

COMPETITOR ACTIVITY
Competitor A: Price cut of 3%
Competitor B: Capacity expansion
Competitor C: Marketing campaign
```

### Trend Analysis

Track performance trends over time:

```
PROFIT TREND (Last 5 Rounds)
Round 1: $18,000
Round 2: $21,000
Round 3: $24,000
Round 4: $25,000
Round 5: $27,000
Trend: ↗️ Improving (+11.1% over 5 rounds)
```

## Advanced Features

### Scenario Selection

Choose from different business scenarios:

#### Beginner Scenarios
- **Stable Market**: Predictable conditions, good for learning basics
- **Growth Market**: Expanding demand, focus on scaling

#### Intermediate Scenarios
- **Competitive Market**: High rivalry, strategic positioning required
- **Technology Disruption**: Innovation and adaptation challenges

#### Advanced Scenarios
- **Economic Recession**: Cost control and survival focus
- **Global Expansion**: International market dynamics

### Save/Load System

```
SAVE/LOAD MENU
═══════════════
1. Quick Save
2. Manual Save
3. Load Game
4. Save to File
5. Load from File

Choose option (1-5): 1
Save created: quicksave_20250101_143022.json
```

**Save Types**:
- **Quick Save**: Fast automatic saves
- **Manual Save**: Named saves with descriptions
- **Auto Save**: Automatic saves every few rounds

### Analytics and Reporting

Access detailed analytics:

```
ANALYTICS MENU
═══════════════
1. View KPI Trends
2. Generate Report
3. Export Data
4. Performance Charts
5. Competitor Analysis

Choose option (1-5): 2
```

**Available Reports**:
- **Financial Report**: Detailed profit/loss analysis
- **Operational Report**: Efficiency and capacity metrics
- **Market Report**: Competitive positioning
- **Comprehensive Report**: All metrics combined

### Leaderboards and Achievements

Track your performance against others:

```
LEADERBOARD - OVERALL PERFORMANCE
═══════════════════════════════════
Rank 1: TechVision Corp     Score: 89.5 ⭐
Rank 2: GlobalTech Inc      Score: 87.2
Rank 3: InnovateNow Ltd     Score: 85.8
Rank 4: Your Company        Score: 82.1 (+2.3 from last round)

ACHIEVEMENTS UNLOCKED
══════════════════════
🏆 Profit Master: Achieved 25% profit margin
💰 Cash Flow King: 5 consecutive positive cash flow rounds
⚡ Efficiency Expert: Operational efficiency above 90%
```

## Tips for Success

### Early Game Strategy (Rounds 1-3)
1. **Focus on Basics**: Ensure positive cash flow
2. **Build Capacity**: Expand gradually to meet demand
3. **Quality First**: Invest in quality to build customer loyalty
4. **Conservative Pricing**: Stay competitive but maintain margins

### Mid Game Strategy (Rounds 4-8)
1. **Scale Operations**: Increase capacity as market grows
2. **Marketing Investment**: Build brand value for premium positioning
3. **Efficiency Focus**: Optimize operations to reduce costs
4. **Monitor Competition**: Respond to competitor actions

### Late Game Strategy (Rounds 9+)
1. **Sustain Growth**: Balance expansion with profitability
2. **Risk Management**: Prepare for economic events
3. **Market Leadership**: Aim for top market share position
4. **Long-term Planning**: Consider end-game objectives

### General Tips
- **Balance is Key**: Don't focus on one metric at expense of others
- **Monitor Trends**: Watch KPI changes over multiple rounds
- **Learn from Mistakes**: Use save/load to try different strategies
- **Adapt to Events**: Market events require quick strategic adjustments
- **Cash Management**: Maintain healthy cash reserves for opportunities

### Common Pitfalls to Avoid
- **Overexpansion**: Don't expand capacity faster than demand grows
- **Price Wars**: Aggressive price cutting hurts profitability
- **Ignoring Quality**: Poor quality leads to customer loss
- **Cash Flow Neglect**: Running out of cash ends the game quickly
- **Competitor Blindness**: Always monitor what rivals are doing

## Troubleshooting

### Common Issues

#### Game Won't Start
```
Error: ModuleNotFoundError: No module named 'modules'
```
**Solution**: Ensure you're running from the project root directory:
```bash
cd /path/to/UseCaseSimulator
python -m modules.ui.console_ui
```

#### Save Files Not Loading
```
Error: Invalid save file format
```
**Solution**:
1. Check if save file is corrupted
2. Try loading from an auto-save
3. Start a new game if all saves are corrupted

#### Performance Issues
**Symptoms**: Game runs slowly, especially with analytics
**Solutions**:
1. Close other applications
2. Reduce chart generation frequency
3. Use simpler report formats
4. Consider upgrading Python version

#### Decision Input Errors
```
Error: Invalid decision format
```
**Solution**: Follow the exact format shown in prompts:
- Prices: decimal numbers (e.g., 105.50)
- Budgets: select from numbered options
- Yes/No: enter 'y' or 'n'

### Getting Help

1. **In-Game Help**: Press 'H' in most menus for context help
2. **Documentation**: Check the docs/ folder for detailed guides
3. **Issue Reports**: Report bugs on GitHub with save files
4. **Community**: Join discussions for strategy tips

### Recovery Options

If you encounter a game-breaking issue:

1. **Quick Save Recovery**: Load from the most recent quick save
2. **Round Back**: Go back 1-2 rounds using save files
3. **Scenario Restart**: Start the same scenario over
4. **New Scenario**: Try a different scenario with similar difficulty

## Next Steps

Now that you understand the basics:

1. **Start Playing**: Launch the game and try the tutorial scenario
2. **Experiment**: Try different strategies and see their outcomes
3. **Learn Analytics**: Use the reporting features to understand performance
4. **Challenge Yourself**: Progress through increasingly difficult scenarios
5. **Share Results**: Compare your performance on leaderboards

Remember, the key to success is learning from each decision and adapting your strategy based on results. Good luck, and enjoy building your business empire!