#!/usr/bin/env python3
"""
FRR BGP Core Pipeline Tracer (Anchor-Only Allow-list Mode)
--------------------------------------------------------------------------------
Uses a path-contraction algorithm to map execution pathways exclusively between
high-level protocol anchors, omitting intermediate functional noise.

Standalone architecture engineered for Apple Silicon macOS.
"""

import os
import re
import sys
import argparse
import logging
from typing import Dict, Set, List
from graphviz import Digraph

# Explicitly append Apple Silicon Homebrew binary layout bounds to PATH
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin" + os.pathsep + "/usr/local/bin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)
logger = logging.getLogger("FRRPipelineTracer")


class FRRPipelineAnalyzer:
    def __init__(self, bgpd_dir: str):
        self.bgpd_dir = bgpd_dir
        self.raw_call_graph: Dict[str, Set[str]] = {}
        self.function_origins: Dict[str, str] = {}
        
        # Strict core pipeline targets (The Explicit Allow-list)
        self.core_anchors = {
            "bgp_read", 
            "bgp_process_packet", 
            "bgp_open_receive", 
            "bgp_update_receive", 
            "bgp_keepalive_receive", 
            "bgp_notification_receive",
            "bgp_event", 
            "bgp_fsm_change_status", 
            "bgp_packet_dump",
            "bgp_attr_parse", 
            "bgp_nlri_parse", 
            "bgp_vty_init"
        }

    def clean_c_code(self, content: str) -> str:
        """Strips out comments cleanly to avoid regex false positives."""
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*', '', content)
        return content

    def build_raw_graph(self):
        """Builds a complete lexical map of the bgpd files inside memory."""
        if not os.path.isdir(self.bgpd_dir):
            logger.error(f"Target path does not exist or is not a directory: {self.bgpd_dir}")
            sys.exit(1)

        func_def_pattern = re.compile(
            r'(?:static\s+|inline\s+)*(?:struct\s+)?\w+\s*\*?\s*(\w+)\s*\([^)]*\)\s*\{', 
            re.MULTILINE
        )
        defun_pattern = re.compile(r'DEFUN\s*\(\s*(\w+)')

        c_files = [f for f in os.listdir(self.bgpd_dir) if f.endswith('.c')]
        logger.info(f"Ingesting {len(c_files)} source files to build complete call graph reference...")

        # Phase 1: Index all declarations
        for filename in c_files:
            filepath = os.path.join(self.bgpd_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = self.clean_c_code(f.read())
                
                for match in func_def_pattern.finditer(content):
                    func_name = match.group(1)
                    if func_name not in self.function_origins:
                        self.function_origins[func_name] = filename
                        self.raw_call_graph[func_name] = set()

                for match in defun_pattern.finditer(content):
                    cmd_name = f"DEFUN_{match.group(1)}"
                    self.function_origins[cmd_name] = filename
                    self.raw_call_graph[cmd_name] = set()

        # Phase 2: Map internal calls using block parsing boundaries
        all_known_funcs = set(self.function_origins.keys())
        token_lookup = {f: f for f in all_known_funcs}
        for func in all_known_funcs:
            if func.startswith("DEFUN_"):
                token_lookup[func.replace("DEFUN_", "")] = func

        call_token_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        for filename in c_files:
            filepath = os.path.join(self.bgpd_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = self.clean_c_code(f.read())
                
                for current_func, origin_file in self.function_origins.items():
                    if origin_file != filename:
                        continue
                        
                    func_escaped = current_func.replace("DEFUN_", "")
                    search_str = func_escaped + r'\s*\([^)]*\)\s*\{' if not current_func.startswith("DEFUN_") else r'DEFUN\s*\(\s*' + func_escaped
                    match = re.search(search_str, content)
                    
                    if not match:
                        continue
                        
                    start_idx = match.end() - 1
                    bracket_count = 1
                    end_idx = start_idx + 1
                    
                    while bracket_count > 0 and end_idx < len(content):
                        if content[end_idx] == '{':
                            bracket_count += 1
                        elif content[end_idx] == '}':
                            bracket_count -= 1
                        end_idx += 1
                        
                    function_scope_body = content[start_idx:end_idx]
                    found_tokens = call_token_pattern.findall(function_scope_body)
                    
                    for token in found_tokens:
                        if token in token_lookup:
                            target_match = token_lookup[token]
                            if target_match != current_func:
                                self.raw_call_graph[current_func].add(target_match)

    def compute_contracted_pipeline(self) -> Digraph:
        """
        Executes a path-contraction traversal sequence.
        Traces connections across intermediate functions to find direct pathways between anchors.
        """
        dot = Digraph(comment='FRR BGP Core Pipeline Trace', format='svg')
        dot.attr(rankdir='LR', splines='true', overlap='false', concentrate='true')
        dot.attr(nodesep='0.6', ranksep='1.5')
        dot.attr('node', fontname='Helvetica-Bold', fontsize='12', shape='box', style='filled,rounded')

        contracted_edges: Set[tuple] = set()
        active_nodes: Set[str] = set()

        logger.info("Computing path contraction transitions across internal logic lines...")

        # Traverse the path out from every anchor point
        for anchor in self.core_anchors:
            # Handle exact name or wrapped DEFUN equivalents
            matching_keys = [k for k in self.raw_call_graph.keys() if anchor in k]
            
            for start_node in matching_keys:
                # Execute Breadth-First Search to isolate downstream target anchors
                queue: List[str] = list(self.raw_call_graph.get(start_node, set()))
                visited: Set[str] = set(queue)
                
                while queue:
                    curr = queue.pop(0)
                    
                    # Check if the function we hit matches any core anchor pattern
                    is_target_anchor = False
                    matched_anchor_name = ""
                    for a in self.core_anchors:
                        if a in curr:
                            is_target_anchor = True
                            matched_anchor_name = curr
                            break
                    
                    if is_target_anchor:
                        contracted_edges.add((start_node, matched_anchor_name))
                        active_nodes.add(start_node)
                        active_nodes.add(matched_anchor_name)
                        # Stop deep execution exploration along this branch to keep tracing concise
                        continue
                        
                    # Expand intermediate components
                    for child in self.raw_call_graph.get(curr, set()):
                        if child not in visited:
                            visited.add(child)
                            queue.append(child)

        # Map active components to their corresponding file groupings
        file_clusters: Dict[str, List[str]] = {}
        for node in active_nodes:
            origin_file = self.function_origins.get(node, "unknown.c")
            file_clusters.setdefault(origin_file, []).append(node)

        # Render layout groupings onto the canvas
        for idx, (filename, nodes) in enumerate(file_clusters.items()):
            with dot.subgraph(name=f"cluster_{idx}") as sub:
                sub.attr(label=filename, color='#34495E', style='rounded,dashed', fontname='Helvetica-Bold', fontsize='12')
                for node in nodes:
                    if "receive" in node or "read" in node or "process" in node:
                        sub.node(node, label=node, fillcolor='#E74C3C', color='#C0392B', fontcolor='white')
                    elif "parse" in node:
                        sub.node(node, label=node, fillcolor='#F39C12', color='#D35400', fontcolor='white')
                    elif "fsm" in node or "event" in node:
                        sub.node(node, label=node, fillcolor='#9B59B6', color='#8E44AD', fontcolor='white')
                    else:
                        sub.node(node, label=node, fillcolor='#3498DB', color='#2980B9', fontcolor='white')

        for edge in contracted_edges:
            dot.edge(edge[0], edge[1], color='#2C3E50', penwidth='1.5', arrowsize='1.0')

        return dot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ultra-clean BGP pipeline trace diagrams.")
    parser.add_argument("--src", required=True, help="Path to frr/bgpd source folder")
    parser.add_argument("--output", default="pipeline_frr_map", help="Output file base filename")

    args = parser.parse_args()

    analyzer = FRRPipelineAnalyzer(args.src)
    analyzer.build_raw_graph()
    
    graph = analyzer.compute_contracted_pipeline()
    
    try:
        output_path = graph.render(args.output, cleanup=True)
        print(f"\n[+] Processing Matrix Output Generation Completed Successfully!")
        print(f"[+] Cleaned Pipeline Diagram exported to: {output_path}\n")
    except Exception as e:
        print(f"\n[-] Error during rendering: {e}")