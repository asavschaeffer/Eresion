# text_based_RPG/data_loader.py
"""
Data loader for configuration-driven game content.

This module loads game data from JSON configuration files, making the system
data-driven rather than hardcoded. It supports hot-reloading and validation.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from shared.action_interfaces import ActionModifier
from shared.data_structures import Entity

@dataclass 
class LocationData:
    """Configuration data for a game location."""
    name: str
    description: str
    safety_level: str
    connections: List[str]
    default_entities: List[str]
    environmental_modifiers: Dict[str, float]
    ambient_description: List[str]

@dataclass
class EntityData:
    """Configuration data for a game entity."""
    name: str
    display_name: str
    type: str
    is_hostile: bool
    is_alive: bool
    stats: Dict[str, float]
    behavior: Dict[str, float] = None
    dialogue: Dict[str, Any] = None
    services: Dict[str, Any] = None
    location_preferences: List[str] = None

class GameDataLoader:
    """
    Loads and manages game configuration data from JSON files.
    
    This replaces hardcoded game content with data-driven configuration,
    making the system more scalable and mod-friendly.
    """
    
    def __init__(self, data_directory: str = None):
        if data_directory is None:
            # Default to data subdirectory
            current_dir = os.path.dirname(__file__)
            self.data_directory = os.path.join(current_dir, "data")
        else:
            self.data_directory = data_directory
        
        # Cached data
        self._locations_cache = None
        self._entities_cache = None
        self._modifiers_cache = None
        
        # Load all data on initialization
        self.reload_all_data()
    
    def reload_all_data(self):
        """Reload all configuration data from files."""
        self._locations_cache = self._load_json_file("locations.json")
        self._entities_cache = self._load_json_file("entities.json")
        self._modifiers_cache = self._load_json_file("action_modifiers.json")
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load and parse a JSON configuration file."""
        filepath = os.path.join(self.data_directory, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: Configuration file {filepath} not found")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {filepath}: {e}")
            return {}
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}
    
    # ========================================================================
    # LOCATION DATA ACCESS
    # ========================================================================
    
    def get_location_data(self, location_id: str) -> Optional[LocationData]:
        """Get configuration data for a specific location."""
        locations = self._locations_cache.get("locations", {})
        location_config = locations.get(location_id)
        
        if not location_config:
            return None
        
        return LocationData(
            name=location_config.get("name", location_id),
            description=location_config.get("description", ""),
            safety_level=location_config.get("safety_level", "neutral"),
            connections=location_config.get("connections", []),
            default_entities=location_config.get("default_entities", []),
            environmental_modifiers=location_config.get("environmental_modifiers", {}),
            ambient_description=location_config.get("ambient_description", [])
        )
    
    def get_all_locations(self) -> Dict[str, LocationData]:
        """Get all location configurations."""
        locations = {}
        location_configs = self._locations_cache.get("locations", {})
        
        for location_id, config in location_configs.items():
            locations[location_id] = LocationData(
                name=config.get("name", location_id),
                description=config.get("description", ""),
                safety_level=config.get("safety_level", "neutral"),
                connections=config.get("connections", []),
                default_entities=config.get("default_entities", []),
                environmental_modifiers=config.get("environmental_modifiers", {}),
                ambient_description=config.get("ambient_description", [])
            )
        
        return locations
    
    def get_travel_time(self, from_location: str, to_location: str) -> float:
        """Get travel time between two locations."""
        travel_times = self._locations_cache.get("location_relationships", {}).get("travel_times", {})
        
        if from_location in travel_times and to_location in travel_times[from_location]:
            return travel_times[from_location][to_location]
        
        # Default travel time if not specified
        return 1.0
    
    def get_weather_effects(self, weather_type: str) -> Dict[str, Any]:
        """Get environmental effects for a weather condition."""
        weather_effects = self._locations_cache.get("weather_effects", {})
        return weather_effects.get(weather_type, {})
    
    def get_time_of_day_effects(self, time_of_day: str) -> Dict[str, Any]:
        """Get environmental effects for a time of day."""
        time_effects = self._locations_cache.get("time_of_day_effects", {})
        return time_effects.get(time_of_day, {})
    
    # ========================================================================
    # ENTITY DATA ACCESS  
    # ========================================================================
    
    def get_entity_data(self, entity_id: str) -> Optional[EntityData]:
        """Get configuration data for a specific entity."""
        entities = self._entities_cache.get("entities", {})
        entity_config = entities.get(entity_id)
        
        if not entity_config:
            return None
        
        return EntityData(
            name=entity_config.get("name", entity_id),
            display_name=entity_config.get("display_name", entity_id),
            type=entity_config.get("type", "unknown"),
            is_hostile=entity_config.get("is_hostile", False),
            is_alive=entity_config.get("is_alive", True),
            stats=entity_config.get("stats", {}),
            behavior=entity_config.get("behavior", {}),
            dialogue=entity_config.get("dialogue", {}),
            services=entity_config.get("services", {}),
            location_preferences=entity_config.get("location_preferences", [])
        )
    
    def create_entity_from_data(self, entity_id: str) -> Optional[Entity]:
        """Create an Entity object from configuration data."""
        entity_data = self.get_entity_data(entity_id)
        if not entity_data:
            return None
        
        entity = Entity(
            name=entity_data.display_name,
            is_hostile=entity_data.is_hostile,
            is_alive=entity_data.is_alive,
            stats=entity_data.stats.copy()
        )
        
        # Add additional data to entity stats for easy access
        if entity_data.behavior:
            entity.stats.update({f"behavior_{k}": v for k, v in entity_data.behavior.items()})
        
        return entity
    
    def get_entities_for_location(self, location_id: str) -> List[Entity]:
        """Get default entities for a specific location."""
        location_data = self.get_location_data(location_id)
        if not location_data:
            return []
        
        entities = []
        for entity_id in location_data.default_entities:
            entity = self.create_entity_from_data(entity_id)
            if entity:
                entities.append(entity)
        
        return entities
    
    def get_entity_dialogue(self, entity_id: str) -> Dict[str, Any]:
        """Get dialogue data for an entity."""
        entity_data = self.get_entity_data(entity_id)
        if not entity_data or not entity_data.dialogue:
            return {}
        
        return entity_data.dialogue
    
    def get_entity_services(self, entity_id: str) -> Dict[str, Any]:
        """Get service capabilities for an entity."""
        entity_data = self.get_entity_data(entity_id)
        if not entity_data or not entity_data.services:
            return {}
        
        return entity_data.services
    
    # ========================================================================
    # MODIFIER DATA ACCESS
    # ========================================================================
    
    def get_modifier_data(self, modifier_name: str) -> Optional[ActionModifier]:
        """Get action modifier configuration."""
        modifiers = self._modifiers_cache.get("action_modifiers", {})
        modifier_config = modifiers.get(modifier_name.upper())
        
        if not modifier_config:
            return None
        
        return ActionModifier(
            name=modifier_config.get("name", modifier_name),
            speed_multiplier=modifier_config.get("speed_multiplier", 1.0),
            damage_multiplier=modifier_config.get("damage_multiplier", 1.0),
            stamina_multiplier=modifier_config.get("stamina_multiplier", 1.0),
            accuracy_multiplier=modifier_config.get("accuracy_multiplier", 1.0),
            stealth_bonus=modifier_config.get("stealth_bonus", 0.0),
            social_bonus=modifier_config.get("social_bonus", 0.0),
            description=modifier_config.get("description", "")
        )
    
    def get_all_modifiers(self) -> Dict[str, ActionModifier]:
        """Get all action modifier configurations."""
        modifiers = {}
        modifier_configs = self._modifiers_cache.get("action_modifiers", {})
        
        for modifier_name, config in modifier_configs.items():
            modifiers[modifier_name] = ActionModifier(
                name=config.get("name", modifier_name),
                speed_multiplier=config.get("speed_multiplier", 1.0),
                damage_multiplier=config.get("damage_multiplier", 1.0),
                stamina_multiplier=config.get("stamina_multiplier", 1.0),
                accuracy_multiplier=config.get("accuracy_multiplier", 1.0),
                stealth_bonus=config.get("stealth_bonus", 0.0),
                social_bonus=config.get("social_bonus", 0.0),
                description=config.get("description", "")
            )
        
        return modifiers
    
    def get_modifier_aliases(self, modifier_name: str) -> List[str]:
        """Get aliases for a specific modifier."""
        modifiers = self._modifiers_cache.get("action_modifiers", {})
        modifier_config = modifiers.get(modifier_name.upper(), {})
        return modifier_config.get("aliases", [])
    
    def get_modifier_by_alias(self, alias: str) -> Optional[ActionModifier]:
        """Find modifier by alias."""
        modifiers = self._modifiers_cache.get("action_modifiers", {})
        
        for modifier_name, config in modifiers.items():
            aliases = config.get("aliases", [])
            if alias.lower() in [a.lower() for a in aliases]:
                return self.get_modifier_data(modifier_name)
        
        return None
    
    def get_contextual_modifier_effects(self, modifier_name: str, context: str) -> Dict[str, float]:
        """Get contextual bonuses for a modifier in a specific situation."""
        contextual_modifiers = self._modifiers_cache.get("contextual_modifiers", {})
        
        # Check environmental context
        environmental = contextual_modifiers.get("environmental", {})
        if context in environmental:
            context_effects = environmental[context]
            if modifier_name.upper() in context_effects:
                return context_effects[modifier_name.upper()]
        
        return {}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def validate_data_integrity(self) -> List[str]:
        """Validate loaded data for consistency and completeness."""
        errors = []
        
        # Validate location connections
        locations = self._locations_cache.get("locations", {})
        for location_id, location_data in locations.items():
            connections = location_data.get("connections", [])
            for connection in connections:
                if connection not in locations:
                    errors.append(f"Location {location_id} connects to unknown location {connection}")
        
        # Validate entity references in locations
        entities = self._entities_cache.get("entities", {})
        for location_id, location_data in locations.items():
            default_entities = location_data.get("default_entities", [])
            for entity_id in default_entities:
                if entity_id not in entities:
                    errors.append(f"Location {location_id} references unknown entity {entity_id}")
        
        return errors
    
    def get_data_statistics(self) -> Dict[str, int]:
        """Get statistics about loaded data."""
        return {
            "locations": len(self._locations_cache.get("locations", {})),
            "entities": len(self._entities_cache.get("entities", {})),
            "modifiers": len(self._modifiers_cache.get("action_modifiers", {})),
            "weather_types": len(self._locations_cache.get("weather_effects", {})),
            "time_periods": len(self._locations_cache.get("time_of_day_effects", {}))
        }
    
    def hot_reload_data(self):
        """Hot-reload data without restarting the application."""
        print("Hot-reloading game data...")
        old_stats = self.get_data_statistics()
        
        self.reload_all_data()
        
        new_stats = self.get_data_statistics()
        print(f"Data reloaded: {old_stats} -> {new_stats}")
        
        # Validate integrity after reload
        errors = self.validate_data_integrity()
        if errors:
            print("Data integrity warnings:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Data integrity check passed.")

# ============================================================================
# GLOBAL DATA LOADER INSTANCE
# ============================================================================

# Create global instance for easy access throughout the application
_global_data_loader = None

def get_data_loader() -> GameDataLoader:
    """Get global data loader instance."""
    global _global_data_loader
    if _global_data_loader is None:
        _global_data_loader = GameDataLoader()
    return _global_data_loader

def reload_game_data():
    """Hot-reload all game data."""
    global _global_data_loader
    if _global_data_loader:
        _global_data_loader.hot_reload_data()
    else:
        _global_data_loader = GameDataLoader()