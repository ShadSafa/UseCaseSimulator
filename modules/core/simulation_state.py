from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from .company import Company
from .market import Market


@dataclass
class SimulationState:
    """Represents the current state of the business simulation."""

    round_number: int
    player_company: Company  # Player's company object
    market: Market  # Market object
    competitors: List[Dict[str, Any]]  # List of competitor companies
    events: List[Dict[str, Any]]  # Active events
    kpis: Dict[str, float]  # Key Performance Indicators
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert GameState to dictionary for serialization."""
        return {
            'round_number': self.round_number,
            'player_company': self.player_company.to_dict() if hasattr(self.player_company, 'to_dict') else self.player_company,
            'market': self.market.to_dict() if hasattr(self.market, 'to_dict') and callable(getattr(self.market, 'to_dict', None)) else self.market,
            'competitors': self.competitors,
            'events': self.events,
            'kpis': self.kpis,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationState':
        """Create SimulationState from dictionary."""
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        data_copy['player_company'] = Company.from_dict(data.get('player_company', {}))
        # Handle market as dict - create Market object from dict
        if 'market' in data_copy and isinstance(data_copy['market'], dict):
            from .market import Market
            data_copy['market'] = Market.from_dict(data_copy['market'])
        return cls(**data_copy)