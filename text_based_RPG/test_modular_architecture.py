# text_based_RPG/test_modular_architecture.py
"""
Comprehensive test suite for the modular Eresion architecture.

This test suite validates:
1. Processor Unit Tests (independent testing)
2. Tokenizer Integration Tests (Strategy pattern validation)
3. Simulation Tests (WorldSimulator validation)  
4. End-to-End Pipeline Tests (full system validation)
"""

import unittest
import time
from unittest.mock import Mock, patch
from typing import List

# Setup paths
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
from text_based_RPG.game_state import GameState, PlayerState, EnvironmentalState, BiometricState
from text_based_RPG.config import Config, StreamConfig
from text_based_RPG.world_simulator import WorldSimulator
from text_based_RPG.tokenizer import ModularTokenizer
from text_based_RPG.stream_processors import (
    PlayerProcessor, BiometricProcessor, EnvironmentalProcessor,
    SocialProcessor, TemporalProcessor
)
from interfaces import Token, TokenType

class TestStreamProcessors(unittest.TestCase):
    """
    Unit tests for individual stream processors.
    
    These tests are completely independent - each processor should only
    need a GameState object and should never import main.py or WorldSimulator.
    """
    
    def setUp(self):
        """Set up test GameState for processor testing."""
        self.game_state = GameState()
        # Set up some test data
        self.game_state.player.location = "Deep Forest"
        self.game_state.player.health_percent = 0.6
        self.game_state.player.stamina_percent = 0.8
        self.game_state.player.in_combat = True
        
    def test_player_processor_independence(self):
        """Test that PlayerProcessor works independently."""
        processor = PlayerProcessor()
        
        # Test domain
        self.assertEqual(processor.get_domain(), "player")
        
        # Test token generation
        tokens = processor.process(self.game_state)
        
        # Validate token structure
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
        
        # Check that all tokens have correct domain
        for token in tokens:
            self.assertEqual(token.metadata["domain"], "player")
            
        # Test specific token types
        token_types = [t.type for t in tokens]
        self.assertIn("LOCATION", token_types)
        self.assertIn("PLAYER_STATE", token_types)
        self.assertIn("COMBAT_STATE", token_types)  # Should be present due to in_combat=True
        
    def test_biometric_processor_independence(self):
        """Test that BiometricProcessor works independently.""" 
        processor = BiometricProcessor()
        
        # Test configuration check
        mock_config = Mock()
        mock_config.streams.biometric_enabled = True
        self.assertTrue(processor.is_enabled(mock_config))
        
        mock_config.streams.biometric_enabled = False
        self.assertFalse(processor.is_enabled(mock_config))
        
        # Test token generation
        tokens = processor.process(self.game_state)
        
        # Validate biometric-specific tokens
        self.assertIsInstance(tokens, list)
        biometric_tokens = [t for t in tokens if t.metadata["domain"] == "biometric"]
        self.assertGreater(len(biometric_tokens), 0)
        
        # Check for expected biometric measurements
        sensor_types = [t.metadata.get("sensor_type") for t in tokens if t.metadata.get("sensor_type")]
        self.assertIn("heart_rate", sensor_types)
        self.assertIn("focus_level", sensor_types)
        
    def test_environmental_processor_independence(self):
        """Test that EnvironmentalProcessor works independently."""
        processor = EnvironmentalProcessor()
        
        tokens = processor.process(self.game_state)
        
        # Check environmental tokens are generated
        env_tokens = [t for t in tokens if t.metadata["domain"] == "environmental"]
        self.assertGreater(len(env_tokens), 0)
        
        # Test location context analysis
        location_tokens = [t for t in tokens if t.type == "LOCATION" and t.metadata["domain"] == "environmental"]
        self.assertGreater(len(location_tokens), 0)
        
        location_token = location_tokens[0]
        self.assertIn("context", location_token.metadata)
        self.assertIn("danger_level", location_token.metadata)

class TestModularTokenizer(unittest.TestCase):
    """
    Integration tests for the ModularTokenizer.
    
    These tests validate the Strategy pattern implementation and ensure
    processors are correctly configured based on configuration.
    """
    
    def test_processor_configuration_strategy(self):
        """Test that processors are configured based on StreamConfig."""
        # Test all streams enabled
        config = Config()
        config.streams = StreamConfig(
            player_enabled=True,
            biometric_enabled=True,
            environmental_enabled=True,
            social_enabled=True,
            temporal_enabled=True
        )
        
        tokenizer = ModularTokenizer(config)
        self.assertEqual(len(tokenizer.processors), 5)
        
        # Test selective stream configuration
        config.streams = StreamConfig(
            player_enabled=True,
            biometric_enabled=False,
            environmental_enabled=True,
            social_enabled=False,
            temporal_enabled=False
        )
        
        tokenizer = ModularTokenizer(config)
        self.assertEqual(len(tokenizer.processors), 2)  # Only player and environmental
        
        # Check processor domains
        domains = [proc.get_domain() for proc in tokenizer.processors]
        self.assertIn("player", domains)
        self.assertIn("environmental", domains)
        self.assertNotIn("biometric", domains)
        self.assertNotIn("social", domains)
        
    def test_token_domain_segregation(self):
        """Test that tokens are properly segregated by domain."""
        config = Config()
        config.debug_tokenization = False  # Disable debug output for testing
        
        tokenizer = ModularTokenizer(config)
        game_state = GameState()
        
        from text_based_RPG.game_state import WorldStateSnapshot
        snapshot = WorldStateSnapshot(game_state=game_state)
        
        tokens = tokenizer.process_world_state(snapshot)
        
        # Group tokens by domain
        token_domains = {}
        for token in tokens:
            domain = token.metadata.get("domain", "unknown")
            if domain not in token_domains:
                token_domains[domain] = []
            token_domains[domain].append(token)
            
        # Verify domain segregation
        self.assertIn("player", token_domains)
        self.assertIn("biometric", token_domains)
        self.assertIn("environmental", token_domains)
        
        # Each domain should have multiple tokens
        for domain, domain_tokens in token_domains.items():
            self.assertGreater(len(domain_tokens), 0, f"Domain {domain} should have tokens")

class TestWorldSimulator(unittest.TestCase):
    """
    Tests for WorldSimulator validation.
    
    These tests ensure WorldSimulator properly mutates GameState based on
    configuration and that mutations are realistic and consistent.
    """
    
    def setUp(self):
        """Set up test configuration and game state."""
        self.config = Config()
        self.simulator = WorldSimulator(self.config)
        self.game_state = GameState()
        
    def test_biometric_simulation_configuration(self):
        """Test biometric simulation respects configuration."""
        # Test with biometric enabled - force a condition that should change heart rate
        self.config.streams.biometric_enabled = True
        self.game_state.player.in_combat = True  # Combat should increase heart rate
        self.game_state.player.health_percent = 0.3  # Low health should increase heart rate more
        
        initial_hr = self.game_state.biometric.heart_rate_bpm
        initial_focus = self.game_state.biometric.player_focus_level
        
        self.simulator.update(self.game_state)
        
        # Heart rate should have increased due to combat + low health
        self.assertGreater(self.game_state.biometric.heart_rate_bpm, initial_hr)
        
        # Focus should have decreased due to combat + low stamina
        self.game_state.player.stamina_percent = 0.2  # Low stamina
        self.simulator.update(self.game_state)
        self.assertLess(self.game_state.biometric.player_focus_level, initial_focus)
        
        # Test with biometric disabled  
        self.config.streams.biometric_enabled = False
        simulator_disabled = WorldSimulator(self.config)
        
        game_state_disabled = GameState()
        game_state_disabled.player.in_combat = True
        game_state_disabled.player.health_percent = 0.1  # Very low health
        initial_hr_disabled = game_state_disabled.biometric.heart_rate_bpm
        
        simulator_disabled.update(game_state_disabled)
        
        # Heart rate should remain unchanged when biometric is disabled, even in combat
        self.assertEqual(game_state_disabled.biometric.heart_rate_bpm, initial_hr_disabled)
        
    def test_combat_simulation_realism(self):
        """Test that combat simulation produces realistic results."""
        result = self.simulator.simulate_player_action(self.game_state, "attack", "Goblin")
        
        # Attack should fail if no goblin present
        self.assertFalse(result["success"])
        
        # Add goblin and test again
        self.game_state.environment.nearby_entities = ["Goblin", "Wolf"]
        result = self.simulator.simulate_player_action(self.game_state, "attack", "Goblin")
        
        # Attack should succeed
        self.assertTrue(result["success"])
        self.assertIn("message", result)
        
        # Player should be in combat and take damage
        self.assertTrue(self.game_state.player.in_combat)
        self.assertLess(self.game_state.player.health_percent, 1.0)
        
    def test_temporal_consistency(self):
        """Test that temporal updates are consistent."""
        initial_time = self.game_state.temporal.total_play_time_s
        initial_timestamp = self.game_state.biometric.irl_timestamp
        
        time.sleep(0.01)  # Small delay
        self.simulator.update(self.game_state)
        
        # Time should have progressed
        self.assertGreater(self.game_state.temporal.total_play_time_s, initial_time)
        self.assertGreater(self.game_state.biometric.irl_timestamp, initial_timestamp)

class TestEndToEndPipeline(unittest.TestCase):
    """
    End-to-End pipeline tests using simulation mode.
    
    These tests validate the complete system integration and ensure
    abilities are generated from multi-domain token patterns.
    """
    
    def test_full_pipeline_integration(self):
        """Test complete pipeline from GameState to ability generation."""
        # Setup configuration with all streams enabled
        config = Config()
        config.simulation_mode = True
        config.debug_tokenization = False
        
        # Create components
        world_simulator = WorldSimulator(config)
        tokenizer = ModularTokenizer(config)
        game_state = GameState()
        
        # Simulate several game turns
        tokens_generated = []
        
        for turn in range(10):
            # Update world
            world_simulator.update(game_state)
            
            # Simulate player action
            if turn % 3 == 0:
                result = world_simulator.simulate_player_action(game_state, "attack", "Goblin") 
            else:
                result = world_simulator.simulate_player_action(game_state, "travel", None)
            
            # Tokenize state
            from text_based_RPG.game_state import WorldStateSnapshot
            snapshot = WorldStateSnapshot(
                game_state=game_state,
                discrete_events=[{"type": "PLAYER_COMMAND", "command": "test"}]
            )
            
            turn_tokens = tokenizer.process_world_state(snapshot)
            tokens_generated.extend(turn_tokens)
            
            # Progress time
            game_state.temporal.turn += 1
            
        # Validate multi-domain token generation
        domains_present = set()
        for token in tokens_generated:
            domain = token.metadata.get("domain")
            if domain:
                domains_present.add(domain)
                
        # Should have tokens from multiple domains
        expected_domains = {"player", "biometric", "environmental", "temporal"}
        self.assertTrue(expected_domains.issubset(domains_present), 
                       f"Missing domains. Present: {domains_present}, Expected: {expected_domains}")
        
        # Should have generated a substantial number of tokens
        self.assertGreater(len(tokens_generated), 20, 
                          "Should generate multiple tokens per turn across domains")
                          
    def test_behavioral_pattern_emergence(self):
        """Test that behavioral patterns emerge from consistent actions."""
        config = Config()
        tokenizer = ModularTokenizer(config)
        world_simulator = WorldSimulator(config)
        game_state = GameState()
        
        # Simulate consistent "aggressive" behavior pattern
        combat_tokens = []
        
        for turn in range(15):  # Enough turns to establish pattern
            # Force combat scenario
            game_state.environment.nearby_entities = ["Goblin"]
            game_state.player.in_combat = True
            game_state.player.action_modifier = "QUICK"  # Consistent modifier
            
            world_simulator.update(game_state)
            
            from text_based_RPG.game_state import WorldStateSnapshot
            snapshot = WorldStateSnapshot(
                game_state=game_state,
                discrete_events=[{"type": "PLAYER_COMMAND", "command": "attack goblin quickly"}]
            )
            
            tokens = tokenizer.process_world_state(snapshot)
            
            # Collect combat and action modifier tokens
            for token in tokens:
                if (token.type == "COMBAT_STATE" or 
                    token.type == "ACTION_MODIFIER"):
                    combat_tokens.append(token)
                    
            game_state.temporal.turn += 1
            
        # Should have consistent pattern of combat + quick modifier tokens
        combat_count = len([t for t in combat_tokens if t.type == "COMBAT_STATE"])
        modifier_count = len([t for t in combat_tokens if t.type == "ACTION_MODIFIER"])
        
        self.assertGreater(combat_count, 10, "Should have multiple combat tokens")
        self.assertGreater(modifier_count, 5, "Should have multiple modifier tokens")

def run_test_suite():
    """Run the complete test suite and report results."""
    print("="*60)
    print("      ERESION MODULAR ARCHITECTURE TEST SUITE")  
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestStreamProcessors,
        TestModularTokenizer, 
        TestWorldSimulator,
        TestEndToEndPipeline
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print("\n" + "="*60)
    print("TEST SUITE RESULTS:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
            
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOVERALL RESULT: {'PASS' if success else 'FAIL'}")
    print("="*60)
    
    return success

if __name__ == "__main__":
    run_test_suite()