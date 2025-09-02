# text_based_RPG/mock_data_providers.py
"""
Mock data providers for Tier 2+ data streams.

This module generates realistic, context-aware mock data for biometric and
environmental sensors to feed the State Pipeline tokenization system.
Supports the existing GameState.biometric structure.
"""

import time
import random
import math
from typing import Dict, Any
# FIXED: No longer imports concrete GameState - uses generic bridge data


class BiometricDataProvider:
    """
    Context-aware biometric data provider.
    
    Generates realistic biometric data that responds intelligently to game state
    (higher heart rate in combat, lower focus when low health, etc.)
    """
    
    def __init__(self):
        self.baseline_hr = 72  # Baseline heart rate
        self.baseline_focus = 0.7  # Baseline focus level
        self.noise_factor = 0.1  # Random variation
        
        # State tracking for realistic trends
        self.hr_trend = 0.0  # Gradual heart rate trend
        self.focus_trend = 0.0  # Gradual focus trend
        self.last_update = time.time()
    
    def update_biometric_data(self, game_state: GameState) -> None:
        """
        Update the existing GameState.biometric with context-aware mock data.
        
        Args:
            game_state: Current game state to update
        """
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Generate context-aware heart rate
        game_state.biometric.heart_rate_bpm = self._generate_heart_rate(game_state, dt)
        
        # Generate context-aware focus level
        game_state.biometric.player_focus_level = self._generate_focus_level(game_state, dt)
        
        # Generate context-aware ambient noise
        game_state.biometric.ambient_noise_db = self._generate_ambient_noise(game_state)
        
        # Update timestamp
        game_state.biometric.irl_timestamp = current_time
    
    def _generate_heart_rate(self, game_state: GameState, dt: float) -> int:
        """Generate realistic heart rate based on game context."""
        target_hr = self.baseline_hr
        
        # Combat significantly increases heart rate
        if game_state.player.in_combat:
            target_hr += 35 + random.uniform(-5, 10)  # 107 ± 5 BPM in combat
        
        # Low health increases stress/heart rate
        if game_state.player.health_percent < 0.3:
            target_hr += 20 * (1.0 - game_state.player.health_percent)  # Up to +20 BPM when near death
        
        # Low stamina increases heart rate (exertion)
        if game_state.player.stamina_percent < 0.4:
            target_hr += 15 * (1.0 - game_state.player.stamina_percent)  # Up to +15 BPM when exhausted
        
        # Environmental factors
        if hasattr(game_state.environment, 'weather'):
            if game_state.environment.weather == "Stormy":
                target_hr += 8  # Stress from bad weather
            elif game_state.environment.weather == "Clear":
                target_hr -= 3  # Calm weather
        
        # Time of day effects
        if hasattr(game_state.environment, 'time_of_day'):
            if game_state.environment.time_of_day in ["Night", "Midnight"]:
                target_hr += 5  # Slightly elevated at night (alertness)
        
        # Gradually trend toward target with realistic physiological response time
        hr_diff = target_hr - game_state.biometric.heart_rate_bpm
        trend_change = hr_diff * min(dt * 2.0, 0.3)  # 2.0 = response rate
        self.hr_trend += trend_change
        
        # Apply trend with natural variation
        new_hr = game_state.biometric.heart_rate_bpm + self.hr_trend * dt
        new_hr += random.uniform(-2, 2)  # Natural beat-to-beat variation
        
        # Clamp to physiologically plausible range
        return max(45, min(180, int(new_hr)))
    
    def _generate_focus_level(self, game_state: GameState, dt: float) -> float:
        """Generate realistic focus level based on game context."""
        target_focus = self.baseline_focus
        
        # Combat can either increase focus (flow state) or decrease it (panic)
        if game_state.player.in_combat:
            if game_state.player.health_percent > 0.6:
                target_focus += 0.2  # Good health = combat focus
            else:
                target_focus -= 0.3  # Low health = panic, reduced focus
        
        # Low health significantly impairs focus
        if game_state.player.health_percent < 0.4:
            target_focus -= 0.4 * (1.0 - game_state.player.health_percent)
        
        # Exhaustion impairs focus
        if game_state.player.stamina_percent < 0.3:
            target_focus -= 0.3 * (1.0 - game_state.player.stamina_percent)
        
        # Session duration affects focus (fatigue over time)
        if hasattr(game_state.temporal, 'session_start_time'):
            session_duration_hours = (time.time() - game_state.temporal.session_start_time) / 3600
            if session_duration_hours > 1.0:
                target_focus -= min(0.2, session_duration_hours * 0.05)  # Gradual fatigue
        
        # Environmental factors
        if hasattr(game_state.environment, 'time_of_day'):
            if game_state.environment.time_of_day in ["Night", "Midnight"]:
                target_focus -= 0.15  # Reduced focus at night
        
        # Gradually trend toward target
        focus_diff = target_focus - game_state.biometric.player_focus_level
        trend_change = focus_diff * min(dt * 1.5, 0.2)  # Slower than heart rate
        self.focus_trend += trend_change
        
        # Apply trend with variation
        new_focus = game_state.biometric.player_focus_level + self.focus_trend * dt
        new_focus += random.uniform(-0.03, 0.03)  # Small natural variation
        
        # Clamp to valid range
        return max(0.0, min(1.0, new_focus))
    
    def _generate_ambient_noise(self, game_state: GameState) -> int:
        """Generate realistic ambient noise level."""
        base_noise = 35  # Quiet environment baseline
        
        # Location affects ambient noise
        location = game_state.player.location.lower()
        if "town" in location or "square" in location:
            base_noise = 50  # Urban ambient noise
        elif "forest" in location:
            base_noise = 25  # Quiet forest
        elif "cave" in location:
            base_noise = 20  # Very quiet cave
        
        # Weather affects noise
        if hasattr(game_state.environment, 'weather'):
            if game_state.environment.weather == "Rain":
                base_noise += 15  # Rain sounds
            elif game_state.environment.weather == "Stormy":
                base_noise += 25  # Storm sounds
        
        # Combat increases noise significantly
        if game_state.player.in_combat:
            base_noise += 20  # Combat sounds
        
        # Add realistic variation
        noise_variation = random.uniform(-5, 8)
        final_noise = base_noise + noise_variation
        
        # Clamp to realistic dB range
        return max(15, min(85, int(final_noise)))


class EnvironmentalDataProvider:
    """
    Enhanced environmental data provider for additional Tier 2 streams.
    
    Extends the basic environmental data with mock sensor readings for
    atmospheric conditions, light levels, etc.
    """
    
    def __init__(self):
        self.base_temperature = 22.0  # Celsius
        self.base_humidity = 45.0  # Percent
        self.base_light_level = 0.7  # Normalized 0-1
    
    def update_environmental_data(self, game_state: GameState) -> Dict[str, Any]:
        """
        Generate additional environmental sensor data.
        
        Returns:
            Dictionary of environmental sensor readings
        """
        # Temperature varies by time of day and weather
        temperature = self.base_temperature
        if hasattr(game_state.environment, 'time_of_day'):
            if game_state.environment.time_of_day in ["Night", "Midnight"]:
                temperature -= 5  # Cooler at night
        
        if hasattr(game_state.environment, 'weather'):
            if game_state.environment.weather == "Rain":
                temperature -= 3
            elif game_state.environment.weather == "Clear":
                temperature += 2
        
        # Add natural variation
        temperature += random.uniform(-2, 2)
        
        # Humidity varies with weather
        humidity = self.base_humidity
        if hasattr(game_state.environment, 'weather'):
            if game_state.environment.weather == "Rain":
                humidity += 25
            elif game_state.environment.weather == "Clear":
                humidity -= 10
        
        humidity = max(20, min(90, humidity + random.uniform(-5, 5)))
        
        # Light level varies by time and location
        light_level = self.base_light_level
        if hasattr(game_state.environment, 'time_of_day'):
            if game_state.environment.time_of_day == "Night":
                light_level = 0.1
            elif game_state.environment.time_of_day == "Midnight":
                light_level = 0.05
            elif game_state.environment.time_of_day == "Morning":
                light_level = 0.6
        
        # Indoor/outdoor affects light
        location = game_state.player.location.lower()
        if "cave" in location:
            light_level *= 0.1  # Very dark
        elif "town" in location:
            light_level += 0.2  # Artificial lighting
        
        return {
            "temperature_celsius": round(temperature, 1),
            "humidity_percent": round(humidity, 1),
            "light_level_normalized": round(max(0.0, min(1.0, light_level)), 2),
            "air_quality_index": random.uniform(0.7, 0.95),  # Generally good air quality
            "barometric_pressure_hpa": 1013 + random.uniform(-10, 10)  # Standard pressure ± variation
        }


class MockSessionProvider:
    """
    Session-level metrics provider for temporal tracking.
    
    Generates session analytics and player behavior metrics that feed
    into the Tier 1 session tracking tokens.
    """
    
    def __init__(self):
        self.session_start = time.time()
        self.action_history = []
        self.last_action_time = time.time()
    
    def update_session_metrics(self, game_state: GameState, action_taken: str = None) -> Dict[str, Any]:
        """
        Update session-level metrics and tracking.
        
        Args:
            game_state: Current game state
            action_taken: Name of action just taken (if any)
            
        Returns:
            Session metrics dictionary
        """
        current_time = time.time()
        
        # Track action if provided
        if action_taken:
            self.action_history.append({
                'action': action_taken,
                'timestamp': current_time,
                'location': game_state.player.location
            })
            self.last_action_time = current_time
        
        # Calculate session metrics
        session_duration = current_time - self.session_start
        actions_this_session = len(self.action_history)
        
        # Calculate recent action frequency
        recent_actions = [a for a in self.action_history if current_time - a['timestamp'] < 60]  # Last minute
        actions_per_minute = len(recent_actions)
        
        # Calculate action diversity
        recent_action_types = set(a['action'] for a in recent_actions)
        action_diversity = len(recent_action_types) / max(1, len(recent_actions)) if recent_actions else 0
        
        # Calculate location exploration
        unique_locations = set(a['location'] for a in self.action_history)
        exploration_score = len(unique_locations) / max(1, actions_this_session)
        
        return {
            "session_duration_s": session_duration,
            "actions_this_session": actions_this_session,
            "actions_per_minute": actions_per_minute,
            "action_diversity_ratio": round(action_diversity, 2),
            "exploration_score": round(exploration_score, 2),
            "time_since_last_action": current_time - self.last_action_time,
            "average_action_interval": session_duration / max(1, actions_this_session)
        }


# Singleton providers for consistent data across the session
_biometric_provider = BiometricDataProvider()
_environmental_provider = EnvironmentalDataProvider()
_session_provider = MockSessionProvider()


def update_mock_data(game_state: GameState, action_taken: str = None) -> Dict[str, Any]:
    """
    Main entry point to update all mock data providers.
    
    This should be called before State Pipeline tokenization to ensure
    fresh, context-aware mock data is available for all processors.
    
    Args:
        game_state: Current game state to update
        action_taken: Name of action just taken (optional)
        
    Returns:
        Dictionary containing all generated mock data for debugging/analysis
    """
    # Update biometric data in the existing GameState.biometric structure
    _biometric_provider.update_biometric_data(game_state)
    
    # Generate additional environmental data
    environmental_data = _environmental_provider.update_environmental_data(game_state)
    
    # Update session metrics
    session_metrics = _session_provider.update_session_metrics(game_state, action_taken)
    
    return {
        "biometric": {
            "heart_rate_bpm": game_state.biometric.heart_rate_bpm,
            "focus_level": game_state.biometric.player_focus_level,
            "ambient_noise_db": game_state.biometric.ambient_noise_db
        },
        "environmental": environmental_data,
        "session": session_metrics
    }


def get_mock_data_summary(game_state: GameState) -> str:
    """
    Get a human-readable summary of current mock data state.
    
    Useful for debugging and validation.
    """
    bio = game_state.biometric
    return (f"Mock Data State: HR={bio.heart_rate_bpm}bpm, "
            f"Focus={bio.player_focus_level:.1f}, "
            f"Noise={bio.ambient_noise_db}dB, "
            f"Combat={game_state.player.in_combat}, "
            f"Health={game_state.player.health_percent:.1f}")