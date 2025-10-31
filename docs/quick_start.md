# Quick Start Guide

Get up and running with the Use Case Simulator in under 5 minutes!

## Installation

### Option 1: pip Install (Fastest)
```bash
pip install usecasesimulator
```

### Option 2: From Source
```bash
git clone https://github.com/ShadSafa/UseCaseSimulator.git
cd UseCaseSimulator
pip install -e .
```

## Launch the Game

```bash
python -m modules.ui.console_ui
```

## Your First Game

### Step 1: Company Setup
```
Welcome to Use Case Simulator!

Enter your company name: My First Company

Choose difficulty:
1. Easy (Stable Market)
2. Medium (Competitive Market)
3. Hard (Economic Recession)

Select (1-3): 1
```

### Step 2: First Round
```
ROUND 1 - DECISION PHASE
═════════════════════════

Current Status:
Revenue: $100,000    Profit: $20,000    Cash: $50,000
Market Share: 15%    Capacity: 80%      Quality: 75%

DECISIONS:
1. Set Price (Current: $100)
2. Expand Capacity (Cost: $50,000)
3. Run Marketing Campaign (Budget options available)
4. Improve Quality (Cost: $15,000)
5. Hire Employees (Cost: $50,000/year)

Enter decisions (comma-separated, e.g., 1,3,5): 1,2
```

### Step 3: Make Decisions
```
Price Decision:
Current price: $100.00
Market average: $98.00
Recommended: $95.00 - $105.00

New price: 102.00

Capacity Expansion:
Current capacity: 1000 units
Utilization: 80%
Cost: $50,000 for 200 additional units

Proceed with expansion? (y/n): y
```

### Step 4: View Results
```
ROUND 1 RESULTS
════════════════

FINANCIAL IMPACT
Revenue: $102,000 (+2.0%)
Costs: $108,000 (+8.0%)
Profit: $14,000 (-30.0%)
Cash: $14,000 (-72.0%)

OPERATIONAL CHANGES
Capacity: 1200 units (+20%)
Utilization: 85%

MARKET RESPONSE
Price Impact: -1% demand
Capacity Impact: +2% market share

Continue to Round 2? (y/n): y
```

## Key Concepts (Quick Reference)

### Core Metrics
- **Revenue**: Sales income
- **Profit**: Revenue minus costs
- **Cash**: Available funds for decisions
- **Market Share**: Your portion of the market
- **Capacity**: Production capability
- **Quality**: Product/service quality

### Decision Types
1. **Pricing**: Balance competitiveness vs. profitability
2. **Capacity**: Expand to meet demand, but watch costs
3. **Marketing**: Build brand value and market share
4. **Quality**: Improve customer satisfaction
5. **Hiring**: Increase operational capability

### Success Indicators
- **Positive Cash Flow**: Don't run out of money!
- **Growing Profit**: Aim for consistent profit increases
- **Market Share Growth**: Expand your market presence
- **High Utilization**: Make efficient use of capacity

## Common First Round Decisions

### Conservative Approach
```
Decisions: 1 (slight price increase), 4 (quality improvement)
Rationale: Build foundation, avoid major expenses
```

### Aggressive Approach
```
Decisions: 2 (capacity expansion), 3 (marketing campaign)
Rationale: Rapid growth, accept short-term cash reduction
```

### Balanced Approach
```
Decisions: 1 (price optimization), 5 (moderate hiring)
Rationale: Steady improvement across multiple areas
```

## Winning Strategies

### Early Game (Rounds 1-3)
- Focus on positive cash flow
- Build quality reputation
- Expand capacity gradually

### Mid Game (Rounds 4-8)
- Invest in marketing
- Optimize pricing strategy
- Monitor competitor actions

### Late Game (Rounds 9+)
- Maximize market share
- Maintain efficiency
- Prepare for market events

## Quick Commands

```
h        - Help
s        - Save game
l        - Load game
q        - Quit
r        - View reports
a        - Analytics menu
```

## Sample Game Session

```
> python -m modules.ui.console_ui
Welcome to Use Case Simulator!

Company Name: TechStart Inc
Difficulty: 1 (Easy)

ROUND 1
Revenue: $100k  Profit: $20k  Cash: $50k

Decisions: 1,2
Price: 102
Expand: Yes

RESULTS
Revenue: $102k (+2%)  Profit: $14k (-30%)  Cash: $14k (-72%)
Market Share: 16.5% (+1.5%)

ROUND 2
Revenue: $106k (+3.9%)  Profit: $18k (+28.6%)  Cash: $32k (+128.6%)
Market Share: 17.8% (+1.3%)

[Game continues...]
```

## Need Help?

- **In-Game Help**: Press 'h' anytime
- **Full Tutorial**: See docs/tutorial.md
- **User Guide**: See docs/user_guide.md
- **Report Issues**: GitHub Issues

## Next Steps

1. Complete your first full game
2. Try different difficulty levels
3. Experiment with various strategies
4. Explore advanced analytics features
5. Create custom scenarios

Happy simulating! 🚀