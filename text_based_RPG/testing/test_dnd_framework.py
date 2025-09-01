#!/usr/bin/env python3
"""
Test script for D&D framework integration and validation.

This script tests the new D&D action framework and validates that it fixes
the core issues identified in the investigation.
"""

import sys
import os
import asyncio
import time
from typing import Dict, List, Any

from text_based_rpg.game_logic.integration import DnDGameEngine
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.config import load_config
from text_based_rpg.data_loader import get_data_loader

class DnDFrameworkTester:
    """
    Comprehensive tester for D&D framework.
    
    Tests all major components and validates improvements over old system.
    """
    
    def __init__(self):
        self.config = load_config()
        self.config.debug_tokenization = True
        self.results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print("="*60)
        print("      D&D FRAMEWORK INTEGRATION TESTS")
        print("="*60)
        
        test_results = {}
        
        # Test 1: System initialization
        print("\n[TEST 1] System Initialization")
        test_results['initialization'] = self.test_system_initialization()
        
        # Test 2: Action parsing and execution
        print("\n[TEST 2] Action Parsing and Execution")
        test_results['action_parsing'] = self.test_action_parsing()
        
        # Test 3: Token generation quality
        print("\n[TEST 3] Token Generation Quality")
        test_results['token_generation'] = self.test_token_generation()
        
        # Test 4: Behavioral signature analysis
        print("\n[TEST 4] Behavioral Signature Analysis")
        test_results['behavioral_signatures'] = self.test_behavioral_signatures()
        
        # Test 5: Data-driven configuration
        print("\n[TEST 5] Data-Driven Configuration")
        test_results['data_driven'] = self.test_data_driven_system()
        
        # Test 6: Performance comparison
        print("\n[TEST 6] Performance Comparison")
        test_results['performance'] = self.test_performance()
        
        # Test 7: Edge cases and error handling
        print("\n[TEST 7] Edge Cases and Error Handling")
        test_results['edge_cases'] = self.test_edge_cases()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY:")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_result in test_results.items():
            status = "PASS" if test_result.get('success', False) else "FAIL"
            print(f"{test_name.upper()}: {status}")
            if not test_result.get('success', False) and test_result.get('error'):
                print(f"  Error: {test_result['error']}")
            
            total_tests += 1
            if test_result.get('success', False):
                passed_tests += 1
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        return test_results
    
    def test_system_initialization(self) -> Dict[str, Any]:
        """Test that all system components initialize correctly."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            # Check components are initialized
            assert engine.dispatcher is not None, "Dispatcher not initialized"
            assert engine.tokenizer is not None, "Tokenizer not initialized"
            assert engine.data_loader is not None, "Data loader not initialized"
            assert engine.context_factory is not None, "Context factory not initialized"
            
            # Check system integrity
            issues = engine.validate_system_integrity()
            
            print(f"✓ System initialized successfully")
            if issues:
                print(f"⚠ Integrity issues found: {len(issues)}")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"  - {issue}")
            else:
                print("✓ System integrity check passed")
            
            return {
                'success': True,
                'components_loaded': True,
                'integrity_issues': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_action_parsing(self) -> Dict[str, Any]:
        """Test action parsing and execution."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            test_commands = [
                "dash", # Travel to Deep Forest first
                "attack goblin quickly",
                "dash", # Travel back to Town Square
                "influence blacksmith respectfully",
                "rest cautiously", 
                "dodge",
                "ready attack"
            ]
            
            parsing_results = []
            
            for command in test_commands:
                print(f"Testing: '{command}'")
                
                start_time = time.time()
                result = engine.process_player_turn(command)
                duration_ms = (time.time() - start_time) * 1000
                
                outcome = result['outcome']
                tokens = result['tokens_generated']
                
                parsing_results.append({
                    'command': command,
                    'success': outcome.success,
                    'tokens_generated': len(tokens),
                    'duration_ms': duration_ms,
                    'message': outcome.message
                })
                
                print(f"  Result: {'SUCCESS' if outcome.success else 'FAILED'}")
                print(f"  Tokens: {len(tokens)}, Time: {duration_ms:.2f}ms")
                
                if not outcome.success:
                    print(f"  Error: {outcome.message}")
            
            # Calculate success rate
            successful_commands = sum(1 for r in parsing_results if r['success'])
            success_rate = successful_commands / len(test_commands)
            
            print(f"✓ Action parsing test completed: {success_rate:.1%} success rate")
            
            return {
                'success': success_rate >= 0.8,  # At least 80% should succeed
                'success_rate': success_rate,
                'results': parsing_results,
                'avg_tokens': sum(r['tokens_generated'] for r in parsing_results) / len(parsing_results)
            }
            
        except Exception as e:
            print(f"✗ Action parsing test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_token_generation(self) -> Dict[str, Any]:
        """Test quality and richness of token generation."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            # Execute a series of actions and analyze token quality
            test_sequence = [
                "attack goblin quickly",
                "dodge cautiously", 
                "rest",
                "influence blacksmith friendly"
            ]
            
            all_tokens = []
            token_analysis = {
                'action_tokens': 0,
                'behavioral_tokens': 0,
                'context_tokens': 0,
                'unique_types': set(),
                'rich_metadata_count': 0
            }
            
            for command in test_sequence:
                result = engine.process_player_turn(command)
                tokens = result['tokens_generated']
                all_tokens.extend(tokens)
                
                for token in tokens:
                    token_analysis['unique_types'].add(token.type)
                    
                    # Count rich metadata (tokens with 5+ metadata fields)
                    if len(token.metadata) >= 5:
                        token_analysis['rich_metadata_count'] += 1
                    
                    # Categorize token types
                    if token.type.endswith('_ACTION'):
                        token_analysis['action_tokens'] += 1
                    elif token.type == 'BEHAVIORAL_SIGNATURE':
                        token_analysis['behavioral_tokens'] += 1
                    else:
                        token_analysis['context_tokens'] += 1
            
            # Quality metrics
            avg_tokens_per_action = len(all_tokens) / len(test_sequence)
            metadata_richness = token_analysis['rich_metadata_count'] / len(all_tokens) if all_tokens else 0
            type_diversity = len(token_analysis['unique_types'])
            
            print(f"✓ Generated {len(all_tokens)} tokens across {len(test_sequence)} actions")
            print(f"  Average tokens per action: {avg_tokens_per_action:.1f}")
            print(f"  Token type diversity: {type_diversity} unique types")
            print(f"  Metadata richness: {metadata_richness:.1%} tokens with rich metadata")
            print(f"  Action tokens: {token_analysis['action_tokens']}")
            print(f"  Behavioral tokens: {token_analysis['behavioral_tokens']}")
            print(f"  Context tokens: {token_analysis['context_tokens']}")
            
            # Success criteria: Rich tokenization
            success = (
                avg_tokens_per_action >= 5.0 and  # At least 5 tokens per action
                metadata_richness >= 0.3 and      # At least 30% rich metadata
                token_analysis['behavioral_tokens'] > 0 and  # Some behavioral analysis
                type_diversity >= 8                # At least 8 different token types
            )
            
            return {
                'success': success,
                'total_tokens': len(all_tokens),
                'avg_tokens_per_action': avg_tokens_per_action,
                'metadata_richness': metadata_richness,
                'type_diversity': type_diversity,
                'token_breakdown': token_analysis
            }
            
        except Exception as e:
            print(f"✗ Token generation test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_behavioral_signatures(self) -> Dict[str, Any]:
        """Test behavioral signature generation and analysis."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            # Test different behavioral styles
            behavioral_tests = [
                ("attack goblin quickly", "aggressive"),
                ("dodge cautiously", "defensive"),
                ("influence blacksmith respectfully", "social"),
                ("rest", "recovery")
            ]
            
            behavioral_data = []
            
            for command, expected_style in behavioral_tests:
                result = engine.process_player_turn(command)
                tokens = result['tokens_generated']
                
                # Find behavioral signature token
                behavioral_token = None
                for token in tokens:
                    if token.type == 'BEHAVIORAL_SIGNATURE':
                        behavioral_token = token
                        break
                
                if behavioral_token:
                    signature = behavioral_token.metadata
                    behavioral_data.append({
                        'command': command,
                        'expected_style': expected_style,
                        'aggression': signature.get('aggression', 0.0),
                        'risk_tolerance': signature.get('risk_tolerance', 0.0),
                        'social_orientation': signature.get('social_orientation', 0.0),
                        'found_signature': True
                    })
                    
                    print(f"'{command}' -> Aggression: {signature.get('aggression', 0.0):.2f}, "
                          f"Risk: {signature.get('risk_tolerance', 0.0):.2f}, "
                          f"Social: {signature.get('social_orientation', 0.0):.2f}")
                else:
                    behavioral_data.append({
                        'command': command,
                        'expected_style': expected_style,
                        'found_signature': False
                    })
                    print(f"'{command}' -> No behavioral signature found")
            
            # Analyze behavioral consistency
            signatures_found = sum(1 for bd in behavioral_data if bd['found_signature'])
            signature_rate = signatures_found / len(behavioral_tests)
            
            # Check if behavioral signatures make sense
            sensible_signatures = 0
            for bd in behavioral_data:
                if not bd['found_signature']:
                    continue
                
                if bd['expected_style'] == 'aggressive' and bd['aggression'] > 0.3:
                    sensible_signatures += 1
                elif bd['expected_style'] == 'defensive' and bd['aggression'] < -0.1:
                    sensible_signatures += 1
                elif bd['expected_style'] == 'social' and bd['social_orientation'] > 0.3:
                    sensible_signatures += 1
                elif bd['expected_style'] == 'recovery' and bd['aggression'] < -0.3:
                    sensible_signatures += 1
            
            sensibility_rate = sensible_signatures / signatures_found if signatures_found else 0
            
            print(f"✓ Behavioral signature test: {signature_rate:.1%} signatures found, "
                  f"{sensibility_rate:.1%} sensible")
            
            return {
                'success': signature_rate >= 0.75 and sensibility_rate >= 0.5,
                'signature_rate': signature_rate,
                'sensibility_rate': sensibility_rate,
                'behavioral_data': behavioral_data
            }
            
        except Exception as e:
            print(f"✗ Behavioral signature test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_data_driven_system(self) -> Dict[str, Any]:
        """Test data-driven configuration system."""
        try:
            data_loader = get_data_loader()
            
            # Test data loading
            stats = data_loader.get_data_statistics()
            print(f"✓ Data loaded: {stats}")
            
            # Test location data
            town_data = data_loader.get_location_data("town_square")
            forest_data = data_loader.get_location_data("deep_forest")
            
            assert town_data is not None, "Town Square data not found"
            assert forest_data is not None, "Deep Forest data not found"
            
            # Test entity data
            blacksmith = data_loader.get_entity_data("blacksmith")
            goblin = data_loader.get_entity_data("goblin")
            
            assert blacksmith is not None, "Blacksmith data not found"
            assert goblin is not None, "Goblin data not found"
            assert not blacksmith.is_hostile, "Blacksmith should not be hostile"
            assert goblin.is_hostile, "Goblin should be hostile"
            
            # Test modifier data
            quick_mod = data_loader.get_modifier_data("QUICK")
            cautious_mod = data_loader.get_modifier_data("CAUTIOUS")
            
            assert quick_mod is not None, "Quick modifier not found"
            assert cautious_mod is not None, "Cautious modifier not found"
            assert quick_mod.speed_multiplier > 1.0, "Quick should increase speed"
            assert cautious_mod.speed_multiplier <= 1.0, "Cautious should not increase speed"
            
            print("✓ Data-driven system validation passed")
            
            return {
                'success': True,
                'data_stats': stats,
                'locations_loaded': stats['locations'] > 0,
                'entities_loaded': stats['entities'] > 0,
                'modifiers_loaded': stats['modifiers'] > 0
            }
            
        except Exception as e:
            print(f"✗ Data-driven system test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test performance improvements."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            # Performance test: process 20 actions and measure timing
            test_commands = [
                "attack goblin", "dodge", "rest", "dash", "influence blacksmith"
            ] * 4  # 20 total commands
            
            timings = []
            token_counts = []
            
            print("Running performance test...")
            start_total = time.time()
            
            for i, command in enumerate(test_commands):
                start_time = time.time()
                result = engine.process_player_turn(command)
                duration_ms = (time.time() - start_time) * 1000
                
                timings.append(duration_ms)
                token_counts.append(len(result.get('tokens_generated', [])))
                
                if (i + 1) % 5 == 0:
                    print(f"  Completed {i+1}/20 actions...")
            
            total_duration = time.time() - start_total
            
            # Performance metrics
            avg_time = sum(timings) / len(timings)
            max_time = max(timings)
            min_time = min(timings)
            avg_tokens = sum(token_counts) / len(token_counts)
            
            # Performance targets from CLAUDE.md
            tokenization_target = 1.0  # < 1ms
            total_turn_target = 10.0   # < 10ms
            
            performance_pass = avg_time < total_turn_target
            
            print(f"✓ Performance test completed:")
            print(f"  Total time: {total_duration:.2f}s for 20 actions")
            print(f"  Average per action: {avg_time:.2f}ms (target: <{total_turn_target}ms)")
            print(f"  Range: {min_time:.2f}ms - {max_time:.2f}ms")
            print(f"  Average tokens per action: {avg_tokens:.1f}")
            print(f"  Performance target: {'PASS' if performance_pass else 'FAIL'}")
            
            return {
                'success': performance_pass,
                'avg_time_ms': avg_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'avg_tokens': avg_tokens,
                'total_actions': len(test_commands),
                'meets_target': performance_pass
            }
            
        except Exception as e:
            print(f"✗ Performance test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and error handling."""
        try:
            game_state = GameState()
            engine = DnDGameEngine(self.config, game_state)
            
            edge_cases = [
                ("", "empty_input"),
                ("qwerty", "gibberish"),
                ("attack nonexistent", "invalid_target"),
                ("fly to moon", "impossible_action"),
                ("attack goblin super extremely mega quickly", "too_many_modifiers"),
                ("ATTACK GOBLIN!!!", "case_and_punctuation")
            ]
            
            edge_results = []
            
            for test_input, case_type in edge_cases:
                print(f"Testing edge case: '{test_input}' ({case_type})")
                
                try:
                    result = engine.process_player_turn(test_input)
                    outcome = result['outcome']
                    
                    # Edge cases should fail gracefully, not crash
                    edge_results.append({
                        'input': test_input,
                        'case_type': case_type,
                        'crashed': False,
                        'graceful_failure': not outcome.success,
                        'helpful_message': bool(outcome.consequences)
                    })
                    
                    print(f"  Result: {'Graceful failure' if not outcome.success else 'Unexpected success'}")
                    if outcome.consequences:
                        print(f"  Help: {outcome.consequences[0]}")
                
                except Exception as e:
                    print(f"  CRASHED: {e}")
                    edge_results.append({
                        'input': test_input,
                        'case_type': case_type,
                        'crashed': True,
                        'error': str(e)
                    })
            
            # Count results
            no_crashes = sum(1 for r in edge_results if not r.get('crashed', True))
            graceful_failures = sum(1 for r in edge_results if r.get('graceful_failure', False))
            helpful_messages = sum(1 for r in edge_results if r.get('helpful_message', False))
            
            crash_rate = (len(edge_cases) - no_crashes) / len(edge_cases)
            help_rate = helpful_messages / len(edge_cases)
            
            print(f"✓ Edge case testing: {no_crashes}/{len(edge_cases)} handled without crashes")
            print(f"  Graceful failures: {graceful_failures}")
            print(f"  Helpful messages: {helpful_messages}")
            
            return {
                'success': crash_rate == 0.0 and help_rate >= 0.5,
                'crash_rate': crash_rate,
                'help_rate': help_rate,
                'edge_results': edge_results
            }
            
        except Exception as e:
            print(f"✗ Edge case test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Run D&D framework tests."""
    tester = DnDFrameworkTester()
    results = tester.run_all_tests()
    
    # Generate summary report
    print("\n" + "="*60)
    print("FINAL ASSESSMENT:")
    print("="*60)
    
    passed_tests = sum(1 for r in results.values() if r.get('success', False))
    total_tests = len(results)
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! D&D framework is ready for deployment.")
    elif passed_tests >= total_tests * 0.8:
        print("✅ Most tests passed. Framework is functional with minor issues.")
    else:
        print("❌ Significant issues found. Framework needs more work.")
    
    print(f"\nTest Results: {passed_tests}/{total_tests} passed")
    
    # Highlight key improvements
    if 'token_generation' in results and results['token_generation'].get('success'):
        avg_tokens = results['token_generation'].get('avg_tokens_per_action', 0)
        print(f"✓ Rich tokenization: {avg_tokens:.1f} tokens per action (vs ~17 in old system)")
    
    if 'performance' in results and results['performance'].get('success'):
        avg_time = results['performance'].get('avg_time_ms', 0)
        print(f"✓ Performance target met: {avg_time:.1f}ms per action")
    
    if 'behavioral_signatures' in results and results['behavioral_signatures'].get('success'):
        sig_rate = results['behavioral_signatures'].get('signature_rate', 0)
        print(f"✓ Behavioral analysis working: {sig_rate:.1%} actions generated signatures")
    
    return results

if __name__ == "__main__":
    main()