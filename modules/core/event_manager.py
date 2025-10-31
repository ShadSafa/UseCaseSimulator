import random
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class EventType(Enum):
    RANDOM = "random"
    SCHEDULED = "scheduled"
    DECISION = "decision"


@dataclass
class Event:
    """Represents a simulation event with its properties and effects."""
    id: str
    name: str
    description: str
    type: EventType
    probability: float
    impact: Dict[str, float]  # Effects on various metrics
    duration: int  # Rounds the event lasts
    conditions: Dict[str, Any]  # Prerequisites for triggering

    def to_dict(self) -> Dict[str, Any]:
        """Convert Event to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'probability': self.probability,
            'impact': self.impact,
            'duration': self.duration,
            'conditions': self.conditions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event from dictionary."""
        data_copy = data.copy()
        data_copy['type'] = EventType(data.get('type', 'random'))
        return cls(**data_copy)


class EventManager:
    """Manages simulation events including generation, processing, and triggering."""

    def __init__(self):
        self.active_events: List[Dict[str, Any]] = []
        self.event_history: List[Dict[str, Any]] = []
        self.event_definitions: Dict[str, Event] = self._load_default_events()

    def _load_default_events(self) -> Dict[str, Event]:
        """Load default event definitions."""
        return {
            'market_crash': Event(
                id='market_crash',
                name='Market Crash',
                description='Sudden market downturn affects all companies',
                type=EventType.RANDOM,
                probability=0.1,
                impact={'revenue': -0.3, 'market_share': -0.1},
                duration=2,
                conditions={}
            ),
            'tech_breakthrough': Event(
                id='tech_breakthrough',
                name='Technology Breakthrough',
                description='New technology increases efficiency',
                type=EventType.RANDOM,
                probability=0.15,
                impact={'efficiency': 0.2, 'costs': -0.1},
                duration=3,
                conditions={}
            ),
            'regulatory_change': Event(
                id='regulatory_change',
                name='Regulatory Change',
                description='New regulations increase compliance costs',
                type=EventType.SCHEDULED,
                probability=1.0,  # Always triggers at round 5
                impact={'costs': 0.15},
                duration=1,
                conditions={'round': 5}
            ),
            'economic_boom': Event(
                id='economic_boom',
                name='Economic Boom',
                description='Strong economic growth boosts demand',
                type=EventType.RANDOM,
                probability=0.2,
                impact={'demand': 0.25, 'revenue': 0.15},
                duration=2,
                conditions={}
            )
        }

    def generate_random_events(self, round_number: int) -> List[Event]:
        """Generate random events based on probabilities and conditions."""
        triggered_events = []

        for event in self.event_definitions.values():
            if event.type == EventType.RANDOM:
                # Check if conditions are met
                if self._check_conditions(event.conditions, round_number):
                    # Roll for probability
                    if random.random() < event.probability:
                        triggered_events.append(event)

        return triggered_events

    def process_scheduled_events(self, round_number: int) -> List[Event]:
        """Process scheduled events that should trigger at specific rounds."""
        triggered_events = []

        for event in self.event_definitions.values():
            if event.type == EventType.SCHEDULED:
                if self._check_conditions(event.conditions, round_number):
                    triggered_events.append(event)

        return triggered_events

    def trigger_event(self, event: Event, round_number: int) -> Dict[str, Any]:
        """Trigger an event and add it to active events."""
        event_data = {
            'event': event.to_dict(),
            'triggered_round': round_number,
            'remaining_duration': event.duration,
            'effects_applied': False
        }

        self.active_events.append(event_data)
        self.event_history.append({
            'event_id': event.id,
            'triggered_round': round_number,
            'timestamp': datetime.now().isoformat()
        })

        return event_data

    def process_active_events(self) -> List[Dict[str, Any]]:
        """Process active events and apply their effects. Returns expired events."""
        expired_events = []

        for event_data in self.active_events[:]:  # Copy to avoid modification during iteration
            event_data['remaining_duration'] -= 1

            if event_data['remaining_duration'] <= 0:
                expired_events.append(event_data)
                self.active_events.remove(event_data)

        return expired_events

    def get_active_event_impacts(self) -> Dict[str, float]:
        """Calculate combined impacts from all active events."""
        total_impacts = {}

        for event_data in self.active_events:
            event_dict = event_data['event']
            impacts = event_dict.get('impact', {})

            for metric, impact in impacts.items():
                if metric not in total_impacts:
                    total_impacts[metric] = 0.0
                total_impacts[metric] += impact

        return total_impacts

    def get_event_history(self) -> List[Dict[str, Any]]:
        """Get the history of triggered events."""
        return self.event_history.copy()

    def get_active_events(self) -> List[Dict[str, Any]]:
        """Get currently active events."""
        return self.active_events.copy()

    def reset(self):
        """Reset the event manager to initial state."""
        self.active_events.clear()
        self.event_history.clear()

    def _check_conditions(self, conditions: Dict[str, Any], round_number: int) -> bool:
        """Check if event conditions are met."""
        for condition_key, condition_value in conditions.items():
            if condition_key == 'round':
                if round_number != condition_value:
                    return False
            elif condition_key == 'min_round':
                if round_number < condition_value:
                    return False
            elif condition_key == 'max_round':
                if round_number > condition_value:
                    return False
            # Add more condition types as needed

        return True

    def add_custom_event(self, event: Event):
        """Add a custom event definition."""
        self.event_definitions[event.id] = event

    def remove_event(self, event_id: str):
        """Remove an event definition."""
        if event_id in self.event_definitions:
            del self.event_definitions[event_id]