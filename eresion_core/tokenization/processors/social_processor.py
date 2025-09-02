# eresion_core/tokenization/processors/social_processor.py
import time
from typing import List, Any, Any

from shared.interfaces import IStreamProcessor, Token, TokenType
# FIXED: No longer imports concrete GameState

class SocialProcessor(IStreamProcessor):
    """
    Processes social interactions and relationship dynamics into tokens.
    
    This processor handles conversations, relationship scores,
    and social context to create meaningful behavioral patterns.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "social"
        
    def process(self, bridge_data: Any) -> List[Token]:
        """
        Convert social state into domain-specific tokens.
        
        Args:
            game_state: Current game state to process
            
        Returns:
            List of tokens representing social interactions and relationships
        """
        tokens = []
        current_time = time.time()
        
        # Recent conversation tokens
        for conversation in game_state.social.recent_conversations[-3:]:  # Last 3 conversations
            time_since = current_time - conversation.get("timestamp", current_time)
            if time_since < 300:  # Only recent conversations (5 minutes)
                tokens.append(Token(
                    type="SOCIAL_INTERACTION",
                    timestamp_s=conversation.get("timestamp", current_time),
                    metadata={
                        "domain": self.get_domain(),
                        "interaction_type": "conversation",
                        "target": conversation.get("target"),
                        "location": conversation.get("location"),
                        "recency": self._categorize_recency(time_since)
                    }
                ))
        
        # Relationship status tokens
        for entity, score in game_state.social.relationship_scores.items():
            relationship_category = self._categorize_relationship(score)
            tokens.append(Token(
                type="RELATIONSHIP_STATUS",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "entity": entity,
                    "score": score,
                    "category": relationship_category,
                    "trend": self._get_relationship_trend(entity, score)
                }
            ))
        
        # Quest status tokens
        for quest in game_state.social.active_quests:
            tokens.append(Token(
                type="QUEST_STATUS",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "quest_name": quest,
                    "status": "active",
                    "quest_type": self._classify_quest_type(quest)
                }
            ))
        
        # Social context token (derived insight)
        social_context = self._analyze_social_context(game_state)
        if social_context:
            tokens.append(Token(
                type="SOCIAL_CONTEXT",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "context_type": social_context["type"],
                    "description": social_context["description"],
                    "factors": social_context["factors"]
                }
            ))
        
        # Social pressure token (if applicable)
        pressure_level = self._calculate_social_pressure(game_state)
        if pressure_level > 0.3:  # Only emit if significant
            tokens.append(Token(
                type="SOCIAL_STATE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "state_type": "social_pressure",
                    "value": pressure_level,
                    "category": self._categorize_pressure_level(pressure_level)
                }
            ))
        
        return tokens
        
    def is_enabled(self, config) -> bool:
        """Check if social processing should be active."""
        return config.streams.social_enabled
        
    def _categorize_recency(self, time_since_seconds: float) -> str:
        """Categorize how recent a conversation was."""
        if time_since_seconds < 60:
            return "immediate"
        elif time_since_seconds < 180:
            return "recent"
        else:
            return "past"
            
    def _categorize_relationship(self, score: float) -> str:
        """Categorize relationship scores into descriptive ranges."""
        if score >= 0.7:
            return "trusted_ally"
        elif score >= 0.3:
            return "friendly"
        elif score >= -0.3:
            return "neutral"
        elif score >= -0.7:
            return "unfriendly"
        else:
            return "hostile"
            
    def _get_relationship_trend(self, entity: str, current_score: float) -> str:
        """
        Determine relationship trend (improving/declining).
        
        In a full implementation, this would track historical scores.
        For now, we use heuristics based on current state.
        """
        # Simplified trend analysis - in practice, you'd track historical data
        if current_score > 0.5:
            return "stable_positive"
        elif current_score < -0.5:
            return "stable_negative"
        else:
            return "fluctuating"
            
    def _classify_quest_type(self, quest_name: str) -> str:
        """Classify quest types for better metadata."""
        quest_lower = quest_name.lower()
        
        if any(word in quest_lower for word in ["kill", "defeat", "slay"]):
            return "combat_quest"
        elif any(word in quest_lower for word in ["deliver", "bring", "take"]):
            return "delivery_quest"
        elif any(word in quest_lower for word in ["find", "locate", "search"]):
            return "exploration_quest"
        elif any(word in quest_lower for word in ["talk", "speak", "convince"]):
            return "social_quest"
        else:
            return "misc_quest"
            
    def _analyze_social_context(self, game_state: GameState) -> dict:
        """
        Analyze the overall social context and dynamics.
        
        Returns emergent social patterns based on multiple factors.
        """
        # Count relationship types
        positive_relationships = sum(1 for score in game_state.social.relationship_scores.values() if score > 0.3)
        negative_relationships = sum(1 for score in game_state.social.relationship_scores.values() if score < -0.3)
        
        # Recent social activity
        recent_conversations = len([
            conv for conv in game_state.social.recent_conversations
            if time.time() - conv.get("timestamp", 0) < 600  # Last 10 minutes
        ])
        
        # Determine context
        if positive_relationships >= 2 and negative_relationships == 0:
            return {
                "type": "socially_connected",
                "description": "Strong positive social network",
                "factors": ["multiple_allies", "no_enemies"]
            }
        elif negative_relationships >= 2:
            return {
                "type": "socially_isolated", 
                "description": "Multiple hostile relationships",
                "factors": ["multiple_enemies", "social_conflict"]
            }
        elif recent_conversations >= 2:
            return {
                "type": "socially_active",
                "description": "High recent social interaction",
                "factors": ["frequent_conversations"]
            }
        elif len(game_state.social.relationship_scores) == 0:
            return {
                "type": "socially_unknown",
                "description": "No established relationships",
                "factors": ["new_environment", "no_relationships"]
            }
            
        return None  # No significant social context
        
    def _calculate_social_pressure(self, game_state: GameState) -> float:
        """
        Calculate social pressure based on relationships and context.
        
        High pressure from hostile relationships, active quests, etc.
        """
        pressure = 0.0
        
        # Pressure from negative relationships
        for score in game_state.social.relationship_scores.values():
            if score < -0.3:
                pressure += abs(score) * 0.3
                
        # Pressure from active quests
        pressure += len(game_state.social.active_quests) * 0.1
        
        # Pressure from recent conflicts (conversations in hostile environments)
        hostile_conversations = 0
        for conv in game_state.social.recent_conversations[-5:]:
            if conv.get("location") == "Deep Forest":  # Dangerous location
                hostile_conversations += 1
        pressure += hostile_conversations * 0.2
        
        return min(1.0, pressure)
        
    def _categorize_pressure_level(self, pressure: float) -> str:
        """Categorize social pressure levels."""
        if pressure < 0.3:
            return "low_pressure"
        elif pressure < 0.6:
            return "moderate_pressure"
        elif pressure < 0.8:
            return "high_pressure"
        else:
            return "extreme_pressure"