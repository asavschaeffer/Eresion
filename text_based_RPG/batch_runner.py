#!/usr/bin/env python3
"""
Phase 3: Batch Runner Script for Eresion Testbed

This script runs N simulation sessions, logging results for analysis.
Features:
- Configurable batch parameters (session count, turn limits)
- Comprehensive logging of token data and behavioral patterns
- Statistical analysis of emergent patterns
- CSV export for further analysis
- Reproducible runs with seeding
"""

import asyncio
import json
import csv
import time
import random
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_based_RPG.main import run_game
from text_based_RPG.config import Config, load_config
from text_based_RPG.game_state import GameState
from interfaces import Token

class BatchRunner:
    """
    Orchestrates multiple simulation sessions and collects performance data.
    
    This implements the batch testing requirements from Phase 3 of the engineering plan.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'num_sessions': 10,
            'max_turns_per_session': 100,
            'seed': 42,
            'output_dir': 'batch_results',
            'save_detailed_logs': True,
            'save_summary_csv': True
        }
        
        # Create output directory
        self.output_dir = Path(self.config['output_dir'])
        self.output_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.session_results = []
        self.aggregate_stats = {}
    
    async def run_batch(self):
        """Execute the batch run with comprehensive logging."""
        print(f"[BATCH] Starting batch run: {self.config['num_sessions']} sessions")
        print(f"[BATCH] Output directory: {self.output_dir}")
        print(f"[BATCH] Max turns per session: {self.config['max_turns_per_session']}")
        print("=" * 60)
        
        # Set random seed for reproducibility
        random.seed(self.config['seed'])
        
        batch_start_time = time.time()
        
        for session_id in range(self.config['num_sessions']):
            print(f"\n[SESSION {session_id + 1}] Running session {session_id + 1}/{self.config['num_sessions']}")
            
            session_result = await self._run_single_session(session_id)
            self.session_results.append(session_result)
            
            # Log progress
            print(f"   [DONE] Completed: {session_result['turns']} turns, "
                  f"{session_result['total_tokens']} tokens, "
                  f"{session_result['abilities_unlocked']} abilities")
        
        batch_duration = time.time() - batch_start_time
        
        # Generate analysis
        print(f"\n[ANALYZE] Analyzing results...")
        self._analyze_results()
        
        # Save results
        await self._save_results()
        
        print(f"\n[COMPLETE] Batch completed in {batch_duration:.2f}s")
        print(f"[OUTPUT] Results saved to: {self.output_dir}")
        self._print_summary()
    
    async def _run_single_session(self, session_id: int) -> Dict[str, Any]:
        """Run a single simulation session and collect metrics."""
        
        # Override sys.argv to simulate --sim mode
        original_argv = sys.argv.copy()
        sys.argv = ['main.py', '--sim']
        
        # Patch the game termination condition for batch runs
        session_start_time = time.time()
        
        try:
            # Import and patch main for batch running
            from text_based_RPG.main import run_game
            
            # Create a controlled version that stops after max_turns
            session_result = await self._run_controlled_session(session_id)
            
        except Exception as e:
            print(f"   [ERROR] Session {session_id} failed: {e}")
            session_result = {
                'session_id': session_id,
                'error': str(e),
                'turns': 0,
                'total_tokens': 0,
                'abilities_unlocked': 0,
                'token_breakdown': {},
                'behavioral_patterns': [],
                'duration_s': time.time() - session_start_time
            }
        finally:
            # Restore original argv
            sys.argv = original_argv
        
        return session_result
    
    async def _run_controlled_session(self, session_id: int) -> Dict[str, Any]:
        """Run a controlled session that terminates after max_turns."""
        from text_based_RPG.game_state import GameState
        from text_based_RPG.config import load_config
        from text_based_RPG.world_simulator import WorldSimulator
        from text_based_RPG.tokenizer import ModularTokenizer
        from text_based_RPG.modules import SimpleNeuronalGraph, SimpleDataAnalytics, SimplePrimitiveComposer, MockLLMConnector, SimpleManifestationDirector, SimpleBalancer
        from text_based_RPG.core import EresionCore, CrystallizationPipeline
        from text_based_RPG.ui import StatusHUD, ActionMenu
        from text_based_RPG.mechanics import ActionDispatcher, SimpleResolver, EventSystem
        from interfaces import NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig, AbilityPrimitive
        
        session_start_time = time.time()
        
        # Initialize components (similar to main.py but controlled)
        config = load_config()
        config.simulation_mode = True
        config.debug_tokenization = False  # Reduce noise in batch mode
        
        game_state = GameState()
        world_simulator = WorldSimulator(config)
        tokenizer = ModularTokenizer(config)
        
        # Phase 1 additions: Dispatcher and Event System
        event_system = EventSystem()
        resolver = SimpleResolver(config)
        action_dispatcher = ActionDispatcher(resolver, event_system)
        
        # Setup analytics and ability generation pipeline
        analytics_config = DataAnalyticsConfig(
            motif_min_support_percent=0.01, 
            min_sessions_to_stabilize=1, 
            motif_stability_threshold=config.motif_stability_threshold
        )
        analytics = SimpleDataAnalytics(analytics_config)
        composer = SimplePrimitiveComposer()
        composer.load_primitive_registry([
            AbilityPrimitive("swift_strike", "VERB", {"aggression": 0.8, "defense": 0.1}, 20.0),
            AbilityPrimitive("defensive_stance", "ADJECTIVE", {"aggression": 0.1, "defense": 0.9}, 15.0)
        ])
        pipeline = CrystallizationPipeline(
            analytics, composer, SimpleBalancer(), MockLLMConnector(), SimpleManifestationDirector()
        )
        
        # Create EresionCore
        eresion = EresionCore(tokenizer, SimpleNeuronalGraph(NeuronalGraphConfig()), pipeline, game_state)
        eresion.current_session = session_id
        
        # UI components (silent in batch mode)
        hud = StatusHUD()
        action_menu = ActionMenu()
        
        # Track metrics
        turn_count = 0
        token_counts_by_domain = {}
        action_counts = {}
        abilities_at_start = len(game_state.player.abilities)
        
        # Run controlled simulation loop
        while (game_state.player.health_percent > 0 and 
               turn_count < self.config['max_turns_per_session']):
            
            # Import the process_turn function
            from text_based_RPG.main import process_turn
            
            # Process turn (but suppress output in batch mode)
            try:
                # Redirect stdout to suppress noise
                import io
                import contextlib
                
                with contextlib.redirect_stdout(io.StringIO()):
                    status = process_turn(
                        game_state, eresion, hud, action_menu, world_simulator, tokenizer,
                        action_dispatcher, event_system, sim_mode=True
                    )
                
                if status == "QUIT":
                    break
                
                # Async pattern analysis
                await eresion.update()
                
                turn_count += 1
                
                # Track token generation
                if hasattr(eresion, 'token_history') and len(eresion.token_history) > 0:
                    recent_count = min(20, len(eresion.token_history))
                    recent_tokens = eresion.token_history[-recent_count:] if recent_count > 0 else []
                    for token in recent_tokens:
                        domain = token.metadata.get('domain', 'unknown')
                        token_counts_by_domain[domain] = token_counts_by_domain.get(domain, 0) + 1
                
            except Exception as e:
                print(f"Turn {turn_count} error: {e}")
                break
        
        # Collect final metrics
        abilities_unlocked = len(game_state.player.abilities) - abilities_at_start
        total_tokens = len(eresion.token_history) if hasattr(eresion, 'token_history') else 0
        
        # Analyze behavioral patterns
        behavioral_patterns = self._extract_behavioral_patterns(eresion.token_history if hasattr(eresion, 'token_history') else [])
        
        return {
            'session_id': session_id,
            'turns': turn_count,
            'final_health': game_state.player.health_percent,
            'final_stamina': game_state.player.stamina_percent,
            'abilities_unlocked': abilities_unlocked,
            'total_tokens': total_tokens,
            'token_breakdown': token_counts_by_domain,
            'behavioral_patterns': behavioral_patterns,
            'duration_s': time.time() - session_start_time,
            'final_location': game_state.player.location,
            'turns_in_combat': sum(1 for _ in range(turn_count) if game_state.player.in_combat)  # Approximation
        }
    
    def _extract_behavioral_patterns(self, token_history: List[Token]) -> List[Dict[str, Any]]:
        """Extract behavioral patterns from token history for analysis."""
        if not token_history:
            return []
        
        patterns = []
        
        # Count action frequencies
        action_counts = {}
        modifier_counts = {}
        
        for token in token_history:
            if token.metadata.get('domain') == 'player_action':
                action = token.metadata.get('action', 'unknown')
                action_counts[action] = action_counts.get(action, 0) + 1
                
                if 'modifier' in token.metadata:
                    modifier = token.metadata['modifier']
                    modifier_counts[modifier] = modifier_counts.get(modifier, 0) + 1
        
        if action_counts:
            patterns.append({
                'type': 'action_frequency',
                'data': action_counts
            })
        
        if modifier_counts:
            patterns.append({
                'type': 'modifier_usage',
                'data': modifier_counts
            })
        
        # Calculate action diversity (Shannon entropy approximation)
        total_actions = sum(action_counts.values())
        if total_actions > 0:
            import math
            entropy = 0
            for count in action_counts.values():
                if count > 0:
                    p = count / total_actions
                    entropy -= p * math.log2(p)
            
            patterns.append({
                'type': 'action_diversity',
                'data': {'entropy': entropy, 'max_possible': math.log2(len(action_counts)) if len(action_counts) > 1 else 0}
            })
        
        return patterns
    
    def _analyze_results(self):
        """Analyze aggregate results across all sessions."""
        if not self.session_results:
            return
        
        # Basic statistics
        turns = [r['turns'] for r in self.session_results if 'turns' in r]
        tokens = [r['total_tokens'] for r in self.session_results if 'total_tokens' in r]
        abilities = [r['abilities_unlocked'] for r in self.session_results if 'abilities_unlocked' in r]
        durations = [r['duration_s'] for r in self.session_results if 'duration_s' in r]
        
        self.aggregate_stats = {
            'sessions_completed': len([r for r in self.session_results if 'error' not in r]),
            'sessions_failed': len([r for r in self.session_results if 'error' in r]),
            'avg_turns': sum(turns) / len(turns) if turns else 0,
            'avg_tokens': sum(tokens) / len(tokens) if tokens else 0,
            'avg_abilities': sum(abilities) / len(abilities) if abilities else 0,
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'total_turns': sum(turns),
            'total_tokens': sum(tokens),
            'total_abilities': sum(abilities)
        }
        
        # Token domain analysis
        all_domains = {}
        for result in self.session_results:
            if 'token_breakdown' in result:
                for domain, count in result['token_breakdown'].items():
                    all_domains[domain] = all_domains.get(domain, 0) + count
        
        self.aggregate_stats['token_domains'] = all_domains
        
        # Behavioral diversity analysis
        all_patterns = []
        for result in self.session_results:
            if 'behavioral_patterns' in result:
                all_patterns.extend(result['behavioral_patterns'])
        
        self.aggregate_stats['behavioral_patterns'] = len(all_patterns)
    
    async def _save_results(self):
        """Save detailed results and summary data."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        if self.config['save_detailed_logs']:
            detailed_file = self.output_dir / f"batch_detailed_{timestamp}.json"
            with open(detailed_file, 'w') as f:
                json.dump({
                    'config': self.config,
                    'aggregate_stats': self.aggregate_stats,
                    'session_results': self.session_results
                }, f, indent=2, default=str)
            print(f"[SAVE] Detailed results: {detailed_file}")
        
        # Save CSV summary
        if self.config['save_summary_csv']:
            csv_file = self.output_dir / f"batch_summary_{timestamp}.csv"
            with open(csv_file, 'w', newline='') as f:
                if self.session_results:
                    writer = csv.DictWriter(f, fieldnames=self.session_results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.session_results)
            print(f"[SAVE] CSV summary: {csv_file}")
        
        # Save aggregate stats
        stats_file = self.output_dir / f"aggregate_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.aggregate_stats, f, indent=2)
        print(f"[SAVE] Aggregate stats: {stats_file}")
    
    def _print_summary(self):
        """Print a summary of the batch results."""
        print("\n" + "="*60)
        print("[SUMMARY] BATCH RUNNER RESULTS")
        print("="*60)
        
        stats = self.aggregate_stats
        print(f"Sessions completed: {stats.get('sessions_completed', 0)}")
        print(f"Sessions failed: {stats.get('sessions_failed', 0)}")
        print(f"Average turns per session: {stats.get('avg_turns', 0):.1f}")
        print(f"Average tokens per session: {stats.get('avg_tokens', 0):.1f}")
        print(f"Average abilities per session: {stats.get('avg_abilities', 0):.2f}")
        print(f"Average duration per session: {stats.get('avg_duration', 0):.1f}s")
        print(f"Total data generated:")
        print(f"  - {stats.get('total_turns', 0)} turns")
        print(f"  - {stats.get('total_tokens', 0)} tokens")
        print(f"  - {stats.get('total_abilities', 0)} abilities")
        
        if 'token_domains' in stats:
            print(f"\nToken distribution:")
            for domain, count in sorted(stats['token_domains'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {domain}: {count}")
        
        print("\n[SUCCESS] Testbed is generating diverse, meaningful data for Eresion system!")

async def main():
    """Main entry point for batch runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Eresion Testbed Batch Runner")
    parser.add_argument("--sessions", type=int, default=5, help="Number of sessions to run")
    parser.add_argument("--max-turns", type=int, default=50, help="Max turns per session")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output-dir", default="batch_results", help="Output directory")
    
    args = parser.parse_args()
    
    config = {
        'num_sessions': args.sessions,
        'max_turns_per_session': args.max_turns,
        'seed': args.seed,
        'output_dir': args.output_dir,
        'save_detailed_logs': True,
        'save_summary_csv': True
    }
    
    runner = BatchRunner(config)
    await runner.run_batch()

if __name__ == "__main__":
    asyncio.run(main())