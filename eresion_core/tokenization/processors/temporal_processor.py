# eresion_core/tokenization/processors/temporal_processor.py
import time
from typing import List, Any, Any

from shared.interfaces import IStreamProcessor, Token, TokenType

class TemporalProcessor(IStreamProcessor):
    """
    Processes time-based patterns and session dynamics into tokens.
    
    This processor handles play session patterns, turn-based timing,
    and temporal behavioral analysis to identify player rhythm patterns.
    
    FIXED: No longer imports concrete GameState - works with generic bridge data.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "temporal"
        
    def process(self, bridge_data: Any) -> List[Token]:
        """
        Convert temporal state into domain-specific tokens.
        
        Args:
            bridge_data: Generic temporal data from game bridge (not concrete GameState)
            
        Returns:
            List of tokens representing temporal patterns and session dynamics
        """
        tokens = []
        current_time = time.time()
        
        # Extract temporal data from bridge (generic approach)
        session_start_time = getattr(bridge_data, 'session_start_time', current_time)
        current_turn = getattr(bridge_data, 'turn', 0)
        actions_this_session = getattr(bridge_data, 'actions_this_session', 0)
        
        # Session duration token
        session_duration = current_time - session_start_time
        session_category = self._categorize_session_duration(session_duration)
        
        tokens.append(Token(
            type="SESSION_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "session_duration",
                "value": session_duration,
                "category": session_category,
                "unit": "seconds"
            }
        ))
        
        # Turn progression token
        turn_pace = self._calculate_turn_pace(current_turn, session_duration)
        tokens.append(Token(
            type="TEMPORAL_PATTERN",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "pattern_type": "turn_progression",
                "current_turn": current_turn,
                "pace": turn_pace,
                "pace_category": self._categorize_turn_pace(turn_pace)
            }
        ))
        
        # Action frequency token
        if session_duration > 0:
            action_rate = actions_this_session / (session_duration / 60.0)  # actions per minute
            tokens.append(Token(
                type="TEMPORAL_PATTERN",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "pattern_type": "action_frequency",
                    "actions_total": actions_this_session,
                    "rate_per_minute": action_rate,
                    "activity_level": self._categorize_activity_level(action_rate)
                }
            ))
        
        # Play style rhythm token (derived insight)
        rhythm_pattern = self._analyze_play_rhythm(current_turn, actions_this_session, session_duration)
        if rhythm_pattern:
            tokens.append(Token(
                type="BEHAVIORAL_PATTERN",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "pattern_type": "play_rhythm",
                    "rhythm_category": rhythm_pattern["category"],
                    "characteristics": rhythm_pattern["characteristics"],
                    "confidence": rhythm_pattern["confidence"]
                }
            ))
        
        # Session phase token
        phase = self._determine_session_phase(session_duration, actions_this_session)
        tokens.append(Token(
            type="SESSION_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "session_phase",
                "phase": phase,
                "phase_characteristics": self._get_phase_characteristics(phase)
            }
        ))
        
        # Temporal consistency token (for pattern detection)
        if current_turn > 10:  # Need some history
            consistency = self._calculate_temporal_consistency(current_turn, session_duration)
            tokens.append(Token(
                type="BEHAVIORAL_PATTERN",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "pattern_type": "temporal_consistency",
                    "consistency_score": consistency,
                    "consistency_category": self._categorize_consistency(consistency)
                }
            ))
        
        return tokens
        
    def is_enabled(self, config) -> bool:
        """Check if temporal processing should be active."""
        return config.streams.temporal_enabled
        
    def _categorize_session_duration(self, duration_seconds: float) -> str:
        """Categorize session duration into meaningful ranges."""
        if duration_seconds < 300:  # 5 minutes
            return "brief"
        elif duration_seconds < 1200:  # 20 minutes
            return "short"
        elif duration_seconds < 3600:  # 1 hour
            return "medium"
        elif duration_seconds < 7200:  # 2 hours
            return "long"
        else:
            return "extended"
            
    def _calculate_turn_pace(self, current_turn: int, session_duration: float) -> float:
        """
        Calculate the pace of turn progression.
        
        Returns turns per minute as a pace metric.
        """
        if session_duration > 0:
            return current_turn / (session_duration / 60.0)
        return 0.0
        
    def _categorize_turn_pace(self, pace: float) -> str:
        """Categorize turn pace into descriptive ranges."""
        if pace < 0.5:
            return "very_slow"
        elif pace < 1.0:
            return "slow" 
        elif pace < 2.0:
            return "moderate"
        elif pace < 4.0:
            return "fast"
        else:
            return "very_fast"
            
    def _categorize_activity_level(self, action_rate: float) -> str:
        """Categorize player activity level based on actions per minute."""
        if action_rate < 0.5:
            return "contemplative"
        elif action_rate < 1.0:
            return "thoughtful"
        elif action_rate < 2.0:
            return "active"
        elif action_rate < 4.0:
            return "energetic"
        else:
            return "frantic"
            
    def _analyze_play_rhythm(self, current_turn: int, actions_this_session: int, session_duration: float) -> dict:
        """
        Analyze the player's temporal rhythm patterns.
        
        This creates emergent behavioral signatures based on timing patterns.
        """
        if session_duration < 60 or current_turn < 5:
            return None  # Not enough data
            
        turn_pace = self._calculate_turn_pace(current_turn, session_duration)
        action_rate = actions_this_session / (session_duration / 60.0)
        
        # Classify rhythm patterns
        if turn_pace > 3.0 and action_rate > 3.0:
            return {
                "category": "rapid_fire",
                "characteristics": ["high_turn_pace", "high_action_rate", "decisive"],
                "confidence": 0.8
            }
        elif turn_pace < 1.0 and action_rate < 1.0:
            return {
                "category": "methodical",
                "characteristics": ["low_turn_pace", "low_action_rate", "contemplative"],
                "confidence": 0.8
            }
        elif abs(turn_pace - action_rate) < 0.5:
            return {
                "category": "steady_rhythm",
                "characteristics": ["consistent_pacing", "balanced_tempo"],
                "confidence": 0.7
            }
        elif turn_pace > action_rate * 1.5:
            return {
                "category": "exploratory",
                "characteristics": ["high_turn_progression", "moderate_actions", "experimental"],
                "confidence": 0.6
            }
        else:
            return {
                "category": "varied_rhythm",
                "characteristics": ["inconsistent_pacing", "adaptive_tempo"],
                "confidence": 0.5
            }
            
    def _determine_session_phase(self, duration: float, actions: int) -> str:
        """Determine what phase of the play session the player is in."""
        if duration < 120:  # First 2 minutes
            return "warmup"
        elif duration < 600:  # First 10 minutes
            return "exploration"
        elif actions / max(1, duration / 60) > 2.0:  # High action rate
            return "engagement"
        elif duration > 1800:  # After 30 minutes
            return "sustained_play"
        else:
            return "development"
            
    def _get_phase_characteristics(self, phase: str) -> List[str]:
        """Get characteristics associated with each session phase."""
        phase_map = {
            "warmup": ["getting_oriented", "learning_controls", "tentative"],
            "exploration": ["discovering_mechanics", "testing_boundaries", "curious"],
            "engagement": ["active_participation", "goal_focused", "committed"],
            "sustained_play": ["deep_involvement", "pattern_established", "experienced"],
            "development": ["skill_building", "strategy_forming", "adaptive"]
        }
        return phase_map.get(phase, ["unknown_phase"])
        
    def _calculate_temporal_consistency(self, current_turn: int, session_duration: float) -> float:
        """
        Calculate how consistent the player's temporal patterns are.
        
        In a full implementation, this would analyze historical timing data.
        For now, we use current session metrics as a proxy.
        """
        # Simplified consistency metric based on current session
        expected_turns = session_duration / 30.0  # Expect ~1 turn per 30 seconds
        
        if expected_turns > 0:
            turn_consistency = 1.0 - abs(current_turn - expected_turns) / max(expected_turns, current_turn)
            return max(0.0, min(1.0, turn_consistency))
        
        return 0.5  # Neutral consistency for edge cases
        
    def _categorize_consistency(self, consistency: float) -> str:
        """Categorize temporal consistency levels."""
        if consistency >= 0.8:
            return "highly_consistent"
        elif consistency >= 0.6:
            return "moderately_consistent"
        elif consistency >= 0.4:
            return "somewhat_inconsistent"
        else:
            return "highly_variable"