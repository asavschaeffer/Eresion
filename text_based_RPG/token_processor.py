# text_based_rpg/token_processor.py
"""
Token processor that connects the mathematical tokenizer to the temporal graph.

This component subscribes to tokenization events and feeds tokens into the 
temporal graph for relationship analysis and pattern detection.
"""

from typing import Dict, Any, List
import time

from text_based_rpg.event_bus import EventBus, GameEvent
from text_based_rpg.mathematical_tokenizer import MathematicalTokenizer
from text_based_rpg.temporal_graph import TemporalGraph
from shared.interfaces import Token


class TokenProcessor:
    """
    Processes tokens from the tokenizer and feeds them to analysis systems.
    
    This component acts as a bridge between the tokenization layer and the
    pattern analysis systems, handling the flow of tokens through the pipeline.
    """
    
    def __init__(self, tokenizer: MathematicalTokenizer, temporal_graph: TemporalGraph, 
                 event_bus: EventBus):
        self.tokenizer = tokenizer
        self.temporal_graph = temporal_graph
        self.event_bus = event_bus
        
        # Processing state
        self.session_id = 1
        self.last_process_time = 0.0
        self.process_interval_s = 1.0  # Process tokens every second
        
        # Statistics
        self.stats = {
            'tokens_processed': 0,
            'tokens_added_to_graph': 0,
            'processing_cycles': 0
        }
        
        # Debug settings
        self.debug = False
        
        # Subscribe to events that indicate we should process tokens
        self.event_bus.subscribe('ProcessTokens', self.handle_process_tokens)
        
        # Set up periodic processing (we'll trigger this manually for now)
        self._setup_periodic_processing()
    
    def set_debug_mode(self, enabled: bool):
        """Enable debug logging."""
        self.debug = enabled
    
    def _setup_periodic_processing(self):
        """Set up periodic token processing."""
        # For now, we'll process tokens after each batch of events
        # In a real system, this might be timer-based
        pass
    
    def handle_process_tokens(self, event: GameEvent):
        """Handle explicit token processing requests."""
        self.process_tokens()
    
    def process_tokens(self):
        """
        Process recent tokens from the tokenizer and feed them to the temporal graph.
        
        This is the main processing loop that moves tokens through the analysis pipeline.
        """
        current_time = time.time()
        
        # Get recent tokens from tokenizer
        recent_tokens = self.tokenizer.get_token_history(limit=100)  # Process last 100 tokens
        
        if not recent_tokens:
            return
        
        # Track which tokens are new since last processing
        tokens_to_process = []
        
        for token in recent_tokens:
            # Simple heuristic: process tokens that are newer than our last process time
            if token.timestamp_s > self.last_process_time:
                tokens_to_process.append(token)
        
        if not tokens_to_process:
            if self.debug:
                print(f"[TokenProcessor] No new tokens to process")
            return
        
        if self.debug:
            print(f"[TokenProcessor] Processing {len(tokens_to_process)} new tokens")
        
        # Feed tokens to temporal graph
        for token in tokens_to_process:
            self.temporal_graph.add_token(token, self.session_id)
            self.stats['tokens_added_to_graph'] += 1
            
            if self.debug:
                intensity = token.metadata.get('intensity', 0.0)
                print(f"[TokenProcessor] Added to graph: {token.type} (intensity: {intensity:.3f})")
        
        self.stats['tokens_processed'] += len(tokens_to_process)
        self.stats['processing_cycles'] += 1
        self.last_process_time = current_time
        
        if self.debug:
            print(f"[TokenProcessor] Processing cycle complete. "
                  f"Total processed: {self.stats['tokens_processed']}")
    
    def force_process_all_tokens(self):
        """
        Force processing of all tokens in tokenizer history.
        
        Useful for batch processing or when we want to ensure all tokens are analyzed.
        """
        if self.debug:
            print(f"[TokenProcessor] Force processing all tokens...")
        
        all_tokens = self.tokenizer.get_token_history()
        
        if not all_tokens:
            return
        
        # Add all tokens to the temporal graph
        for token in all_tokens:
            self.temporal_graph.add_token(token, self.session_id)
            self.stats['tokens_added_to_graph'] += 1
        
        self.stats['tokens_processed'] += len(all_tokens)
        self.stats['processing_cycles'] += 1
        self.last_process_time = time.time()
        
        if self.debug:
            print(f"[TokenProcessor] Force processed {len(all_tokens)} tokens")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.stats,
            'current_session': self.session_id,
            'last_process_time': self.last_process_time,
            'tokenizer_tokens': len(self.tokenizer.get_token_history()),
            'graph_nodes': len(self.temporal_graph.nodes),
            'graph_edges': sum(len(edges) for edges in self.temporal_graph.edges.values())
        }
    
    def start_new_session(self):
        """Start a new session for both tokenizer and graph."""
        self.session_id += 1
        self.temporal_graph.start_new_session()
        
        if self.debug:
            print(f"[TokenProcessor] Started new session: {self.session_id}")
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a comprehensive analysis summary."""
        tokenizer_stats = self.tokenizer.get_statistics()
        graph_stats = self.temporal_graph.get_statistics()
        processor_stats = self.get_statistics()
        
        return {
            'tokenizer': tokenizer_stats,
            'temporal_graph': graph_stats,
            'processor': processor_stats,
            'pipeline_health': {
                'tokens_in_pipeline': tokenizer_stats['total_tokens'],
                'tokens_in_graph': graph_stats['tokens_processed'],
                'processing_ratio': processor_stats['tokens_added_to_graph'] / max(1, tokenizer_stats['total_tokens']),
                'motifs_detected': graph_stats['motifs_detected'],
                'strong_edges': graph_stats.get('strong_edges', 0)
            }
        }