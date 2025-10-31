from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from .ranking_system import RankingSystem, RankingResult, RankingCriteria
import json
import os


@dataclass
class LeaderboardEntry:
    """Entry in the leaderboard."""
    company_id: str
    company_name: str
    score: float
    rank: int
    criteria: str
    achieved_at: datetime
    metadata: Dict[str, Any]


@dataclass
class Achievement:
    """Achievement for reaching milestones."""
    name: str
    description: str
    criteria: Dict[str, Any]
    icon: str
    rarity: str  # "common", "rare", "epic", "legendary"


class Leaderboard:
    """Manages leaderboards and achievements for the simulation."""

    def __init__(self, persistence_file: str = "data/leaderboard.json"):
        self.persistence_file = persistence_file
        self.ranking_system = RankingSystem()
        self.leaderboards: Dict[str, List[LeaderboardEntry]] = {}
        self.achievements: Dict[str, List[Achievement]] = {}
        self.historical_data: List[Dict[str, Any]] = []

        # Initialize default leaderboards
        self._initialize_default_leaderboards()
        self._initialize_achievements()

        # Load persisted data
        self._load_data()

    def _initialize_default_leaderboards(self):
        """Initialize default leaderboard categories."""
        self.leaderboards = {
            'overall': [],
            'financial': [],
            'operational': [],
            'market': [],
            'customer': [],
            'weekly': [],
            'monthly': []
        }

    def _initialize_achievements(self):
        """Initialize achievement definitions."""
        self.achievements = {
            'financial': [
                Achievement(
                    name="Profit Master",
                    description="Achieve profit margin above 25%",
                    criteria={"profit_margin": 0.25},
                    icon="💰",
                    rarity="rare"
                ),
                Achievement(
                    name="Cash Flow King",
                    description="Maintain positive cash flow for 5 consecutive rounds",
                    criteria={"consecutive_positive_cash_flow": 5},
                    icon="💸",
                    rarity="epic"
                ),
                Achievement(
                    name="ROI Champion",
                    description="Achieve ROI above 30%",
                    criteria={"roi": 0.30},
                    icon="📈",
                    rarity="legendary"
                )
            ],
            'operational': [
                Achievement(
                    name="Efficiency Expert",
                    description="Achieve operational efficiency above 90%",
                    criteria={"operational_efficiency": 0.90},
                    icon="⚡",
                    rarity="rare"
                ),
                Achievement(
                    name="Quality Guru",
                    description="Maintain quality index above 95%",
                    criteria={"quality_index": 0.95},
                    icon="⭐",
                    rarity="epic"
                )
            ],
            'market': [
                Achievement(
                    name="Market Leader",
                    description="Achieve market share above 30%",
                    criteria={"market_share": 0.30},
                    icon="👑",
                    rarity="legendary"
                ),
                Achievement(
                    name="Brand Builder",
                    description="Build brand value above 100",
                    criteria={"brand_value": 100},
                    icon="🏷️",
                    rarity="rare"
                )
            ],
            'customer': [
                Achievement(
                    name="Customer Champion",
                    description="Achieve customer satisfaction above 90%",
                    criteria={"customer_satisfaction": 0.90},
                    icon="😊",
                    rarity="epic"
                )
            ]
        }

    def update_leaderboard(self, companies_data: List[Dict[str, Any]],
                          market_data: Dict[str, Any],
                          category: str = "overall") -> List[LeaderboardEntry]:
        """Update a specific leaderboard category.

        Args:
            companies_data: List of company data
            market_data: Market conditions
            category: Leaderboard category to update

        Returns:
            Updated leaderboard entries
        """
        if category not in self.leaderboards:
            raise ValueError(f"Unknown leaderboard category: {category}")

        # Get rankings based on category
        criteria_map = {
            'overall': RankingCriteria.OVERALL_SCORE,
            'financial': RankingCriteria.FINANCIAL_PERFORMANCE,
            'operational': RankingCriteria.OPERATIONAL_EFFICIENCY,
            'market': RankingCriteria.MARKET_POSITION,
            'customer': RankingCriteria.CUSTOMER_SATISFACTION
        }

        criteria = criteria_map.get(category, RankingCriteria.OVERALL_SCORE)
        rankings = self.ranking_system.rank_companies(companies_data, market_data, criteria)

        # Convert to leaderboard entries
        entries = []
        for result in rankings:
            entry = LeaderboardEntry(
                company_id=result.company_id,
                company_name=result.company_name,
                score=result.score,
                rank=result.rank,
                criteria=category,
                achieved_at=datetime.now(),
                metadata={
                    'criteria_scores': result.criteria_scores,
                    'percentile': result.percentile,
                    'trend': result.trend
                }
            )
            entries.append(entry)

        self.leaderboards[category] = entries

        # Update time-based leaderboards
        self._update_time_based_leaderboards(entries, category)

        # Save data
        self._save_data()

        return entries

    def _update_time_based_leaderboards(self, entries: List[LeaderboardEntry], category: str):
        """Update weekly and monthly leaderboards."""
        now = datetime.now()

        # Weekly leaderboard (reset every Monday)
        week_start = now - timedelta(days=now.weekday())
        week_key = week_start.strftime("%Y-%U")

        # Monthly leaderboard (reset every 1st of month)
        month_key = now.strftime("%Y-%m")

        # Update weekly
        if 'weekly' not in self.leaderboards:
            self.leaderboards['weekly'] = []

        weekly_entries = [e for e in self.leaderboards['weekly'] if e.metadata.get('week') == week_key]
        weekly_entries.extend(entries)
        # Keep top entries for the week
        weekly_entries.sort(key=lambda x: x.score, reverse=True)
        self.leaderboards['weekly'] = weekly_entries[:10]  # Top 10

        # Mark with week
        for entry in self.leaderboards['weekly']:
            entry.metadata['week'] = week_key

        # Update monthly (similar logic)
        if 'monthly' not in self.leaderboards:
            self.leaderboards['monthly'] = []

        monthly_entries = [e for e in self.leaderboards['monthly'] if e.metadata.get('month') == month_key]
        monthly_entries.extend(entries)
        monthly_entries.sort(key=lambda x: x.score, reverse=True)
        self.leaderboards['monthly'] = monthly_entries[:10]

        for entry in self.leaderboards['monthly']:
            entry.metadata['month'] = month_key

    def get_leaderboard(self, category: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get leaderboard entries for a category.

        Args:
            category: Leaderboard category
            limit: Maximum number of entries to return

        Returns:
            List of leaderboard entries
        """
        if category not in self.leaderboards:
            return []

        return self.leaderboards[category][:limit]

    def get_company_rank(self, company_id: str, category: str = "overall") -> Optional[LeaderboardEntry]:
        """Get a company's rank in a specific leaderboard.

        Args:
            company_id: Company ID
            category: Leaderboard category

        Returns:
            Leaderboard entry for the company, or None if not found
        """
        leaderboard = self.get_leaderboard(category, limit=1000)  # Get all entries
        for entry in leaderboard:
            if entry.company_id == company_id:
                return entry
        return None

    def check_achievements(self, company_data: Dict[str, Any],
                          kpi_data: Dict[str, float]) -> List[Achievement]:
        """Check if a company has unlocked any achievements.

        Args:
            company_data: Company data
            kpi_data: Current KPI values

        Returns:
            List of newly unlocked achievements
        """
        unlocked = []
        company_id = company_data['id']

        # Check each achievement category
        for category, achievements in self.achievements.items():
            for achievement in achievements:
                if self._check_achievement_criteria(achievement, kpi_data, company_data):
                    # Check if already unlocked (would need persistence for this)
                    unlocked.append(achievement)

        return unlocked

    def _check_achievement_criteria(self, achievement: Achievement,
                                  kpi_data: Dict[str, float],
                                  company_data: Dict[str, Any]) -> bool:
        """Check if achievement criteria are met."""
        for criterion, value in achievement.criteria.items():
            if criterion in kpi_data:
                if kpi_data[criterion] < value:
                    return False
            elif criterion in company_data:
                if company_data[criterion] < value:
                    return False
            else:
                # Special criteria handling
                if not self._check_special_criteria(criterion, value, company_data):
                    return False

        return True

    def _check_special_criteria(self, criterion: str, value: Any, company_data: Dict[str, Any]) -> bool:
        """Check special achievement criteria."""
        if criterion == "consecutive_positive_cash_flow":
            # Would need historical data to check consecutive rounds
            # Placeholder implementation
            return False

        return False

    def get_company_achievements(self, company_id: str) -> List[Achievement]:
        """Get all achievements unlocked by a company."""
        # In a real implementation, this would query a database
        # For now, return empty list
        return []

    def get_leaderboard_stats(self) -> Dict[str, Any]:
        """Get statistics about the leaderboards."""
        stats = {
            'total_categories': len(self.leaderboards),
            'categories': {}
        }

        for category, entries in self.leaderboards.items():
            if entries:
                scores = [e.score for e in entries]
                stats['categories'][category] = {
                    'total_entries': len(entries),
                    'top_score': max(scores),
                    'average_score': sum(scores) / len(scores),
                    'last_updated': entries[0].achieved_at.isoformat()
                }
            else:
                stats['categories'][category] = {
                    'total_entries': 0,
                    'top_score': 0,
                    'average_score': 0,
                    'last_updated': None
                }

        return stats

    def get_historical_performance(self, company_id: str, category: str = "overall",
                                 days: int = 30) -> List[Dict[str, Any]]:
        """Get historical performance data for a company.

        Args:
            company_id: Company ID
            category: Leaderboard category
            days: Number of days to look back

        Returns:
            List of historical performance data points
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        history = []
        for data_point in self.historical_data:
            if data_point['timestamp'] < cutoff_date:
                continue

            entries = data_point.get('leaderboards', {}).get(category, [])
            company_entry = next((e for e in entries if e['company_id'] == company_id), None)

            if company_entry:
                history.append({
                    'date': data_point['timestamp'].isoformat(),
                    'rank': company_entry['rank'],
                    'score': company_entry['score'],
                    'category': category
                })

        return history

    def _save_data(self):
        """Save leaderboard data to file."""
        try:
            os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)

            data = {
                'leaderboards': {},
                'historical_data': self.historical_data,
                'last_updated': datetime.now().isoformat()
            }

            # Convert leaderboard entries to serializable format
            for category, entries in self.leaderboards.items():
                data['leaderboards'][category] = [
                    {
                        'company_id': e.company_id,
                        'company_name': e.company_name,
                        'score': e.score,
                        'rank': e.rank,
                        'criteria': e.criteria,
                        'achieved_at': e.achieved_at.isoformat(),
                        'metadata': e.metadata
                    } for e in entries
                ]

            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving leaderboard data: {e}")

    def _load_data(self):
        """Load leaderboard data from file."""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)

                # Restore leaderboards
                for category, entries_data in data.get('leaderboards', {}).items():
                    entries = []
                    for entry_data in entries_data:
                        entry = LeaderboardEntry(
                            company_id=entry_data['company_id'],
                            company_name=entry_data['company_name'],
                            score=entry_data['score'],
                            rank=entry_data['rank'],
                            criteria=entry_data['criteria'],
                            achieved_at=datetime.fromisoformat(entry_data['achieved_at']),
                            metadata=entry_data['metadata']
                        )
                        entries.append(entry)
                    self.leaderboards[category] = entries

                # Restore historical data
                self.historical_data = data.get('historical_data', [])

        except Exception as e:
            print(f"Error loading leaderboard data: {e}")

    def export_leaderboard(self, category: str, format: str = "json") -> str:
        """Export leaderboard data.

        Args:
            category: Leaderboard category to export
            format: Export format ("json" or "csv")

        Returns:
            Exported data as string
        """
        entries = self.get_leaderboard(category, limit=1000)

        if format == "json":
            data = {
                'category': category,
                'exported_at': datetime.now().isoformat(),
                'entries': [
                    {
                        'rank': e.rank,
                        'company_name': e.company_name,
                        'score': e.score,
                        'achieved_at': e.achieved_at.isoformat()
                    } for e in entries
                ]
            }
            return json.dumps(data, indent=2)

        elif format == "csv":
            lines = ["Rank,Company Name,Score,Achieved At"]
            for e in entries:
                lines.append(f"{e.rank},{e.company_name},{e.score},{e.achieved_at.isoformat()}")
            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")