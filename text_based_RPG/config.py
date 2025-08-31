# text_based_RPG/config.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
from pathlib import Path

@dataclass
class StreamConfig:
    """Configuration for which data streams are enabled."""
    player_enabled: bool = True
    biometric_enabled: bool = True
    environmental_enabled: bool = True
    social_enabled: bool = True
    temporal_enabled: bool = True
    
@dataclass
class PerformanceConfig:
    """Performance and timing configuration."""
    tokenization_target_ms: float = 1.0
    graph_update_target_ms: float = 2.0
    music_generation_target_ms: float = 5.0
    pattern_mining_target_ms: float = 100.0
    ability_generation_target_s: float = 1.0
    
@dataclass
class Config:
    """Master configuration object for the entire Eresion system."""
    streams: StreamConfig = field(default_factory=StreamConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # File paths
    save_file_path: str = "eresion_save.json"
    config_file_path: str = "config.json"
    
    # Simulation settings  
    simulation_mode: bool = False
    simulation_speed_multiplier: float = 1.0
    
    # Analytics settings
    motif_stability_threshold: float = 0.7
    session_window_turns: int = 50
    
    # Debug settings
    debug_tokenization: bool = False
    debug_pattern_detection: bool = False
    debug_ability_generation: bool = False
    debug_performance: bool = False

def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from JSON file with sane defaults.
    
    Args:
        config_path: Path to config file. If None, uses default path.
        
    Returns:
        Config object with loaded or default values.
    """
    config = Config()
    
    if config_path is None:
        config_path = config.config_file_path
        
    config_file = Path(config_path)
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                
            # Update StreamConfig
            if 'streams' in data:
                stream_data = data['streams']
                for key, value in stream_data.items():
                    if hasattr(config.streams, key):
                        setattr(config.streams, key, value)
                        
            # Update PerformanceConfig
            if 'performance' in data:
                perf_data = data['performance']
                for key, value in perf_data.items():
                    if hasattr(config.performance, key):
                        setattr(config.performance, key, value)
                        
            # Update top-level Config fields
            for key, value in data.items():
                if key not in ['streams', 'performance'] and hasattr(config, key):
                    setattr(config, key, value)
                    
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            print("Using default configuration.")
            
    return config

def save_config(config: Config, config_path: Optional[str] = None) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Config object to save
        config_path: Path to save config file. If None, uses config.config_file_path.
    """
    if config_path is None:
        config_path = config.config_file_path
        
    # Convert dataclasses to dict for JSON serialization
    config_dict = {
        'streams': {
            'player_enabled': config.streams.player_enabled,
            'biometric_enabled': config.streams.biometric_enabled,
            'environmental_enabled': config.streams.environmental_enabled,
            'social_enabled': config.streams.social_enabled,
            'temporal_enabled': config.streams.temporal_enabled,
        },
        'performance': {
            'tokenization_target_ms': config.performance.tokenization_target_ms,
            'graph_update_target_ms': config.performance.graph_update_target_ms,
            'music_generation_target_ms': config.performance.music_generation_target_ms,
            'pattern_mining_target_ms': config.performance.pattern_mining_target_ms,
            'ability_generation_target_s': config.performance.ability_generation_target_s,
        },
        'save_file_path': config.save_file_path,
        'config_file_path': config.config_file_path,
        'simulation_mode': config.simulation_mode,
        'simulation_speed_multiplier': config.simulation_speed_multiplier,
        'motif_stability_threshold': config.motif_stability_threshold,
        'session_window_turns': config.session_window_turns,
        'debug_tokenization': config.debug_tokenization,
        'debug_pattern_detection': config.debug_pattern_detection,
        'debug_ability_generation': config.debug_ability_generation,
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save config to {config_path}: {e}")