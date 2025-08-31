"""
Game Data: Entity Stats and Configuration

This module contains all entity definitions, stats, and game balance data.
Separating this from mechanics.py allows for data-driven entity creation
and easier balance adjustments.
"""

from dataclasses import dataclass
from typing import Dict, Any
from .mechanics import Entity

# Entity stat templates
ENTITY_STATS = {
    "goblin": {
        "health": 30,
        "max_health": 30,
        "attack_power": 8,
        "defense": 2,
        "agility": 6,
        "is_hostile": True,
        "is_alive": True,
        "behavior_type": "aggressive",
        "threat_level": 1
    },
    "wolf": {
        "health": 25,
        "max_health": 25,
        "attack_power": 12,
        "defense": 1,
        "agility": 8,
        "is_hostile": True,
        "is_alive": True,
        "behavior_type": "pack_hunter",
        "threat_level": 2
    },
    "bandit": {
        "health": 40,
        "max_health": 40,
        "attack_power": 10,
        "defense": 3,
        "agility": 5,
        "is_hostile": True,
        "is_alive": True,
        "behavior_type": "tactical",
        "threat_level": 2
    },
    "merchant": {
        "health": 20,
        "max_health": 20,
        "attack_power": 2,
        "defense": 1,
        "agility": 3,
        "is_hostile": False,
        "is_alive": True,
        "behavior_type": "friendly",
        "relationship_score": 0
    },
    "villager": {
        "health": 15,
        "max_health": 15,
        "attack_power": 1,
        "defense": 0,
        "agility": 4,
        "is_hostile": False,
        "is_alive": True,
        "behavior_type": "neutral",
        "relationship_score": 0
    },
    "guard": {
        "health": 50,
        "max_health": 50,
        "attack_power": 15,
        "defense": 5,
        "agility": 4,
        "is_hostile": False,  # Neutral unless provoked
        "is_alive": True,
        "behavior_type": "lawful",
        "relationship_score": 5
    }
}

# Location-based entity spawn tables
LOCATION_ENTITIES = {
    "Forest": ["goblin", "wolf"],
    "Mountain Path": ["bandit", "wolf"],
    "Town Square": ["merchant", "villager", "guard"],
    "Village": ["villager", "merchant"],
    "Wilderness": ["wolf", "bandit"],
    "Cave": ["goblin"],
    "Crossroads": ["merchant", "bandit"]
}

# Behavioral patterns for different entity types
BEHAVIOR_PATTERNS = {
    "aggressive": {
        "attack_chance": 0.7,
        "flee_threshold": 0.2,  # Health % at which they flee
        "special_actions": ["RECKLESS_ATTACK"]
    },
    "pack_hunter": {
        "attack_chance": 0.6,
        "flee_threshold": 0.3,
        "pack_bonus": True,  # Gets stronger when multiple wolves present
        "special_actions": ["COORDINATED_STRIKE"]
    },
    "tactical": {
        "attack_chance": 0.5,
        "flee_threshold": 0.4,
        "uses_terrain": True,
        "special_actions": ["DEFENSIVE_STANCE", "FEINT"]
    },
    "friendly": {
        "attack_chance": 0.0,
        "flee_threshold": 0.8,
        "trading": True,
        "dialogue_topics": ["trade", "rumors", "weather"]
    },
    "neutral": {
        "attack_chance": 0.1,  # Only if severely threatened
        "flee_threshold": 0.6,
        "dialogue_topics": ["local_news", "directions", "weather"]
    },
    "lawful": {
        "attack_chance": 0.2,  # Only if laws are broken
        "flee_threshold": 0.1,
        "protects_civilians": True,
        "dialogue_topics": ["law", "safety", "threats"]
    }
}

def create_entity(entity_type: str, name: str = None) -> Entity:
    """
    Factory function to create entities with proper stats from data.
    
    Args:
        entity_type: Type of entity from ENTITY_STATS keys
        name: Optional custom name, defaults to entity_type
    
    Returns:
        Entity instance with proper stats applied
    """
    if entity_type not in ENTITY_STATS:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    stats = ENTITY_STATS[entity_type].copy()
    entity_name = name or entity_type.title()
    
    return Entity(
        name=entity_name,
        is_hostile=stats["is_hostile"],
        is_alive=stats["is_alive"],
        stats=stats
    )

def get_location_entities(location: str) -> list:
    """Get list of entity types that can spawn in a location."""
    return LOCATION_ENTITIES.get(location, [])

def get_entity_behavior(entity: Entity) -> dict:
    """Get behavior pattern for an entity based on its behavior_type."""
    behavior_type = entity.stats.get("behavior_type", "neutral")
    return BEHAVIOR_PATTERNS.get(behavior_type, BEHAVIOR_PATTERNS["neutral"])