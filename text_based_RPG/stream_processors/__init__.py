# text_based_RPG/stream_processors/__init__.py
"""
Stream processors for the Eresion modular tokenization system.

Each processor is responsible for converting one domain of GameState
into relevant tokens with appropriate metadata.
"""

from .player_processor import PlayerProcessor
from .biometric_processor import BiometricProcessor
from .environmental_processor import EnvironmentalProcessor
from .social_processor import SocialProcessor
from .temporal_processor import TemporalProcessor

__all__ = [
    'PlayerProcessor',
    'BiometricProcessor', 
    'EnvironmentalProcessor',
    'SocialProcessor',
    'TemporalProcessor'
]