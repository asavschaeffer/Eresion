# text_based_RPG/dnd_dispatcher.py
"""
D&D Action Registry and Dispatcher.

This module replaces the hardcoded ActionDispatcher with a pluggable registry
system that supports the new D&D action framework with enhanced natural language
parsing and fallback mechanisms.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from text_based_rpg.game_logic.actions import (
    BaseDnDAction, AttackAction, DashAction, DodgeAction, 
    InfluenceAction, ReadyAction, RestAction
)
from shared.action_interfaces import (
    ActionModifier, ActionTarget, ModifierRegistry, TargetResolver,
    IActionContext
)
from shared.data_structures import ActionOutcome, ParsedInput

@dataclass
class ActionParseResult:
    """Result of parsing user input into structured action components."""
    action: Optional[BaseDnDAction] = None
    target: Optional[ActionTarget] = None
    modifier: Optional[ActionModifier] = None
    raw_input: str = ""
    confidence: float = 0.0
    parse_errors: List[str] = None

class DnDActionRegistry:
    """
    Registry of available D&D actions with natural language mapping.
    
    This replaces the hardcoded action handlers with a pluggable system
    that supports aliases, synonyms, and natural language variations.
    """
    
    def __init__(self):
        self.actions: Dict[str, BaseDnDAction] = {}
        self.aliases: Dict[str, str] = {}
        self.synonyms: Dict[str, Set[str]] = {}
        self.modifier_registry = ModifierRegistry()
        
        # Register core D&D actions
        self._register_core_actions()
        self._setup_aliases_and_synonyms()
    
    def _register_core_actions(self):
        """Register the core D&D action implementations."""
        core_actions = [
            AttackAction(),
            DashAction(), 
            DodgeAction(),
            InfluenceAction(),
            ReadyAction(),
            RestAction()
        ]
        
        for action in core_actions:
            self.register_action(action)
    
    def _setup_aliases_and_synonyms(self):
        """Setup natural language aliases and synonyms for actions."""
        
        # Attack synonyms
        self.add_synonyms("Attack", {
            "fight", "hit", "strike", "engage", "assault", "battle", "combat"
        })
        
        # Dash synonyms (movement)
        self.add_synonyms("Dash", {
            "travel", "move", "go", "run", "walk", "journey", "head"
        })
        
        # Dodge synonyms (defense)
        self.add_synonyms("Dodge", {
            "defend", "block", "guard", "parry", "brace", "shield"
        })
        
        # Influence synonyms (social)
        self.add_synonyms("Influence", {
            "talk", "speak", "chat", "converse", "persuade", "convince", 
            "discuss", "negotiate", "socialize"
        })
        
        # Rest synonyms (recovery)
        self.add_synonyms("Rest", {
            "sleep", "recover", "heal", "wait", "relax", "recuperate"
        })
        
        # Ready synonyms (preparation)
        self.add_synonyms("Ready", {
            "prepare", "wait", "anticipate", "watch", "guard"
        })
    
    def register_action(self, action: BaseDnDAction):
        """Register a new action in the registry."""
        action_name = action.name.lower()
        self.actions[action_name] = action
        
        # Self-reference for exact matches
        self.aliases[action_name] = action_name
        if action_name not in self.synonyms:
            self.synonyms[action_name] = set()
    
    def add_synonyms(self, action_name: str, synonyms: Set[str]):
        """Add synonyms for an action."""
        action_key = action_name.lower()
        if action_key not in self.synonyms:
            self.synonyms[action_key] = set()
        
        # Add bidirectional mapping
        self.synonyms[action_key].update(syn.lower() for syn in synonyms)
        
        # Create aliases for quick lookup
        for synonym in synonyms:
            self.aliases[synonym.lower()] = action_key
    
    def get_action(self, action_name: str) -> Optional[BaseDnDAction]:
        """Get action by name or synonym."""
        key = action_name.lower()
        
        # Direct lookup
        if key in self.actions:
            return self.actions[key]
        
        # Alias lookup
        if key in self.aliases:
            canonical_name = self.aliases[key]
            return self.actions.get(canonical_name)
        
        return None
    
    def get_all_actions(self) -> Dict[str, BaseDnDAction]:
        """Get all registered actions."""
        return self.actions.copy()
    
    def get_available_actions_for_context(self, contexts: Dict[str, Any]) -> List[BaseDnDAction]:
        """Get actions that can be executed with current contexts."""
        available = []
        
        for action in self.actions.values():
            required_contexts = action.get_required_contexts()
            if all(ctx in contexts for ctx in required_contexts):
                available.append(action)
        
        return available
    
    def suggest_actions(self, partial_input: str) -> List[str]:
        """Suggest actions based on partial input."""
        partial = partial_input.lower().strip()
        suggestions = []
        
        # Exact prefix matches
        for name in self.actions.keys():
            if name.startswith(partial):
                suggestions.append(name)
        
        # Alias prefix matches
        for alias in self.aliases.keys():
            if alias.startswith(partial) and alias not in suggestions:
                suggestions.append(alias)
        
        return sorted(suggestions)

class EnhancedInputParser:
    """
    Enhanced input parser with natural language processing and fallback mechanisms.
    
    This parser implements the hybrid approach: sophisticated natural language
    parsing with structured fallback when parsing fails.
    """
    
    def __init__(self, action_registry: DnDActionRegistry, target_resolver: TargetResolver):
        self.registry = action_registry
        self.target_resolver = target_resolver
        self.modifier_registry = action_registry.modifier_registry
        
        # Precompiled regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for parsing efficiency."""
        # Pattern for extracting modifiers
        modifier_words = "|".join(self.modifier_registry.get_all_modifiers().keys()).lower()
        self.modifier_pattern = re.compile(rf'\b({modifier_words})\b', re.IGNORECASE)
        
        # Pattern for extracting quoted targets
        self.quoted_target_pattern = re.compile(r'"([^"]+)"')
        
        # Pattern for command structure: [modifier] action [target] [modifier]
        self.command_structure_pattern = re.compile(
            r'^(?:(quickly|carefully|cautiously|powerfully|stealthily|friendly|respectfully)\s+)?'
            r'(\w+)'
            r'(?:\s+(?:the\s+)?(\w+))?'
            r'(?:\s+(quickly|carefully|cautiously|powerfully|stealthily|friendly|respectfully))?$',
            re.IGNORECASE
        )
    
    def parse_input(self, raw_input: str, context: IActionContext) -> ActionParseResult:
        """
        Parse user input into structured action components.
        
        Uses sophisticated natural language processing with confidence scoring.
        """
        if not raw_input or not raw_input.strip():
            return ActionParseResult(
                raw_input=raw_input,
                parse_errors=["Empty input"]
            )
        
        cleaned_input = raw_input.strip().lower()
        result = ActionParseResult(raw_input=raw_input)
        
        try:
            # Step 1: Extract action verb
            action, action_confidence = self._extract_action(cleaned_input)
            if not action:
                result.parse_errors = [f"Could not identify action in '{raw_input}'"]
                return result
            
            # Step 2: Extract target
            target = self._extract_target(cleaned_input, context)
            
            # Step 3: Extract modifier
            modifier = self._extract_modifier(cleaned_input)
            
            # Step 4: Calculate overall confidence
            confidence = action_confidence
            if target and target.is_valid:
                confidence *= 1.2
            if modifier:
                confidence *= 1.1
            
            result.action = action
            result.target = target
            result.modifier = modifier
            result.confidence = min(1.0, confidence)
            
            return result
            
        except Exception as e:
            result.parse_errors = [f"Parsing error: {str(e)}"]
            return result
    
    def _extract_action(self, input_text: str) -> Tuple[Optional[BaseDnDAction], float]:
        """Extract action with confidence scoring."""
        words = input_text.split()
        
        # Try each word as potential action
        for i, word in enumerate(words):
            action = self.registry.get_action(word)
            if action:
                # Higher confidence for earlier words in sentence
                confidence = max(0.7, 1.0 - (i * 0.1))
                return action, confidence
        
        # Try partial matches for fuzzy matching
        for word in words:
            suggestions = self.registry.suggest_actions(word)
            if suggestions:
                best_match = suggestions[0]
                action = self.registry.get_action(best_match)
                if action:
                    return action, 0.6  # Lower confidence for partial matches
        
        return None, 0.0
    
    def _extract_target(self, input_text: str, context: IActionContext) -> Optional[ActionTarget]:
        """Extract and validate target from input."""
        # Try quoted targets first
        quoted_match = self.quoted_target_pattern.search(input_text)
        if quoted_match:
            target_name = quoted_match.group(1)
            return self.target_resolver.resolve_target(target_name)
        
        # Try structured pattern matching
        structure_match = self.command_structure_pattern.match(input_text)
        if structure_match and structure_match.group(3):
            target_name = structure_match.group(3)
            return self.target_resolver.resolve_target(target_name)
        
        # Try entity name recognition
        available_entities = context.combat.get_hostile_entities() + context.combat.get_friendly_entities()
        entity_names = [entity.name.lower() for entity in available_entities]
        
        words = input_text.split()
        for word in words:
            if word in entity_names:
                return self.target_resolver.resolve_target(word)
        
        # Try partial entity name matches
        for word in words:
            for entity_name in entity_names:
                if entity_name.startswith(word) or word in entity_name:
                    return self.target_resolver.resolve_target(entity_name)
        
        return None
    
    def _extract_modifier(self, input_text: str) -> Optional[ActionModifier]:
        """Extract modifier from input text."""
        matches = self.modifier_pattern.findall(input_text)
        if matches:
            # Use the first modifier found
            modifier_name = matches[0].upper()
            return self.modifier_registry.get_modifier(modifier_name)
        
        return None
    
    def get_fallback_suggestions(self, failed_input: str, context: IActionContext) -> List[str]:
        """Generate helpful suggestions when parsing fails."""
        suggestions = []
        
        # Suggest available actions
        available_actions = self.registry.get_available_actions_for_context({
            'combat': context.combat,
            'movement': context.movement,
            'resources': context.resources,
            'social': context.social,
            'state': context.state,
            'environment': context.environment,
            'buffs': context.buffs
        })
        
        if available_actions:
            action_names = [action.name for action in available_actions[:5]]
            suggestions.append(f"Available actions: {', '.join(action_names)}")
        
        # Suggest available targets
        hostile_entities = context.combat.get_hostile_entities()
        friendly_entities = context.combat.get_friendly_entities()
        
        if hostile_entities:
            hostile_names = [e.name for e in hostile_entities]
            suggestions.append(f"Hostile targets: {', '.join(hostile_names)}")
        
        if friendly_entities:
            friendly_names = [e.name for e in friendly_entities]
            suggestions.append(f"Friendly targets: {', '.join(friendly_names)}")
        
        # Suggest modifiers
        modifiers = list(self.modifier_registry.get_all_modifiers().keys())[:4]
        suggestions.append(f"Available modifiers: {', '.join(modifiers).lower()}")
        
        return suggestions

class DnDActionDispatcher:
    """
    D&D Action Dispatcher that replaces the old hardcoded system.
    
    This dispatcher uses the registry pattern with natural language parsing
    and provides both free-text and structured fallback interfaces.
    """
    
    def __init__(self, context: IActionContext):
        self.context = context
        self.registry = DnDActionRegistry()
        self.parser = EnhancedInputParser(
            self.registry, 
            TargetResolver(context.combat, context.social)
        )
    
    def dispatch_action(self, raw_input: str) -> ActionOutcome:
        """
        Dispatch user input to appropriate D&D action.
        
        This is the main entry point that replaces the old ActionDispatcher.dispatch().
        """
        # Parse the input
        parse_result = self.parser.parse_input(raw_input, self.context)
        
        # If parsing failed, provide helpful feedback
        if not parse_result.action:
            return self._handle_parse_failure(parse_result)
        
        # Execute the action with appropriate contexts
        try:
            required_contexts = parse_result.action.get_required_contexts()
            action_contexts = self._build_action_contexts(required_contexts)
            
            outcome = parse_result.action.execute(
                action_contexts,
                parse_result.target,
                parse_result.modifier
            )
            
            # Add parse confidence to outcome for debugging
            if hasattr(outcome, 'metadata'):
                outcome.metadata['parse_confidence'] = parse_result.confidence
            
            return outcome
            
        except Exception as e:
            return ActionOutcome(
                success=False,
                message=f"Error executing {parse_result.action.name}: {str(e)}"
            )
    
    def _handle_parse_failure(self, parse_result: ActionParseResult) -> ActionOutcome:
        """Handle parsing failures with helpful suggestions."""
        error_msg = "I don't understand that command."
        
        if parse_result.parse_errors:
            error_msg = parse_result.parse_errors[0]
        
        # Get suggestions
        suggestions = self.parser.get_fallback_suggestions(parse_result.raw_input, self.context)
        
        consequences = suggestions[:3]  # Limit to avoid overwhelming output
        
        return ActionOutcome(
            success=False,
            message=error_msg,
            consequences=consequences
        )
    
    def _build_action_contexts(self, required_contexts: List[str]) -> Dict[str, Any]:
        """Build the context dictionary that the action needs."""
        contexts = {}
        
        context_map = {
            'combat': self.context.combat,
            'movement': self.context.movement,
            'resources': self.context.resources,
            'social': self.context.social,
            'state': self.context.state,
            'environment': self.context.environment,
            'buffs': self.context.buffs
        }
        
        for context_name in required_contexts:
            if context_name in context_map:
                contexts[context_name] = context_map[context_name]
        
        return contexts
    
    def get_guided_interface(self) -> Dict[str, Any]:
        """
        Get structured interface for 'lazy mode' when natural language fails.
        
        This provides the fallback structured interface discussed in the plan.
        """
        available_actions = self.registry.get_available_actions_for_context({
            'combat': self.context.combat,
            'movement': self.context.movement,
            'resources': self.context.resources,
            'social': self.context.social,
            'state': self.context.state,
            'environment': self.context.environment,
            'buffs': self.context.buffs
        })
        
        # Get available targets
        hostile_entities = self.context.combat.get_hostile_entities()
        friendly_entities = self.context.combat.get_friendly_entities()
        all_entities = hostile_entities + friendly_entities
        
        # Get available modifiers
        modifiers = self.registry.modifier_registry.get_all_modifiers()
        
        return {
            'actions': [(action.name, action.description) for action in available_actions],
            'targets': [(entity.name, 'hostile' if entity.is_hostile else 'friendly') 
                       for entity in all_entities],
            'modifiers': [(name, mod.description) for name, mod in modifiers.items()],
            'examples': [
                "attack goblin quickly",
                "dash to town square",
                "influence blacksmith respectfully",
                "rest cautiously",
                "dodge"
            ]
        }
    
    def dispatch_structured_input(self, action_name: str, target_name: str = None, 
                                 modifier_name: str = None) -> ActionOutcome:
        """
        Dispatch structured input from guided interface.
        
        This is the 'lazy mode' fallback when natural language parsing fails.
        """
        # Build structured input
        parts = [action_name]
        if target_name:
            parts.append(target_name)
        if modifier_name:
            parts.append(modifier_name)
        
        structured_input = " ".join(parts)
        
        # Use the normal dispatch mechanism
        return self.dispatch_action(structured_input)