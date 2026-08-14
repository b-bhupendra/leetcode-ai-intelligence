"""
Curriculum Ontology: Controlled Vocabularies, Normalization & Alias Mappers
"""

import re
from typing import Optional, Set, Dict, List
from curriculum_schema_v2 import Representation, Mechanism, OptimizationObjective

# Alias and synonym maps for robust ontology normalization
REPRESENTATION_ALIASES: Dict[str, Representation] = {
    "array": Representation.ARRAY_1D,
    "array_1d": Representation.ARRAY_1D,
    "1d array": Representation.ARRAY_1D,
    "vector": Representation.ARRAY_1D,
    "matrix": Representation.ARRAY_2D,
    "array_2d": Representation.ARRAY_2D,
    "grid": Representation.ARRAY_2D,
    "interval": Representation.INTERVAL_1D,
    "interval_1d": Representation.INTERVAL_1D,
    "intervals": Representation.INTERVAL_1D,
    "ranges": Representation.INTERVAL_1D,
    "graph": Representation.GRAPH_ADJACENCY,
    "graph_adjacency": Representation.GRAPH_ADJACENCY,
    "tree": Representation.TREE_BINARY,
    "tree_binary": Representation.TREE_BINARY,
    "binary tree": Representation.TREE_BINARY,
    "string": Representation.STRING_TOKENS,
    "string_tokens": Representation.STRING_TOKENS,
    "tokens": Representation.STRING_TOKENS,
    "linked list": Representation.LINKED_LIST,
    "linked_list": Representation.LINKED_LIST,
    "bitmask": Representation.STATE_BITMASK,
    "state_bitmask": Representation.STATE_BITMASK,
    "heap": Representation.HEAP_TREE,
    "hash_table": Representation.HASH_TABLE,
    "hash table": Representation.HASH_TABLE
}

MECHANISM_ALIASES: Dict[str, Mechanism] = {
    "sort_start": Mechanism.SORT_START,
    "sort by start": Mechanism.SORT_START,
    "sort by start time": Mechanism.SORT_START,
    "sort_end": Mechanism.SORT_END,
    "sort by end": Mechanism.SORT_END,
    "sort by finish time": Mechanism.SORT_END,
    "earliest finish time": Mechanism.SORT_END,
    "two_pointer": Mechanism.TWO_POINTER_CONVERGE,
    "two pointer": Mechanism.TWO_POINTER_CONVERGE,
    "two_pointer_converge": Mechanism.TWO_POINTER_CONVERGE,
    "sliding_window": Mechanism.SLIDING_WINDOW,
    "sliding window": Mechanism.SLIDING_WINDOW,
    "greedy": Mechanism.GREEDY_SELECTION,
    "greedy_selection": Mechanism.GREEDY_SELECTION,
    "greedy choice": Mechanism.GREEDY_SELECTION,
    "min_heap": Mechanism.MIN_HEAP,
    "min heap": Mechanism.MIN_HEAP,
    "minimum heap": Mechanism.MIN_HEAP,
    "max_heap": Mechanism.MAX_HEAP,
    "max heap": Mechanism.MAX_HEAP,
    "sweep_line": Mechanism.SWEEP_LINE,
    "sweep line": Mechanism.SWEEP_LINE,
    "event points": Mechanism.SWEEP_LINE,
    "monotonic_stack": Mechanism.MONOTONIC_STACK,
    "monotonic stack": Mechanism.MONOTONIC_STACK,
    "dp_tabulation": Mechanism.DP_TABULATION,
    "tabulation": Mechanism.DP_TABULATION,
    "bottom up dp": Mechanism.DP_TABULATION,
    "dp_memoization": Mechanism.DP_MEMOIZATION,
    "memoization": Mechanism.DP_MEMOIZATION,
    "top down dp": Mechanism.DP_MEMOIZATION,
    "dfs": Mechanism.DFS_RECURSION,
    "dfs_recursion": Mechanism.DFS_RECURSION,
    "bfs": Mechanism.BFS_QUEUE,
    "bfs_queue": Mechanism.BFS_QUEUE,
    "binary_search": Mechanism.BINARY_SEARCH,
    "binary search": Mechanism.BINARY_SEARCH,
    "prefix_sum": Mechanism.PREFIX_SUM,
    "prefix sum": Mechanism.PREFIX_SUM,
    "union_find": Mechanism.UNION_FIND,
    "dsu": Mechanism.UNION_FIND
}

OBJECTIVE_ALIASES: Dict[str, OptimizationObjective] = {
    "maximize_count": OptimizationObjective.MAXIMIZE_COUNT,
    "maximize count": OptimizationObjective.MAXIMIZE_COUNT,
    "max events": OptimizationObjective.MAXIMIZE_COUNT,
    "minimize_removals": OptimizationObjective.MINIMIZE_REMOVALS,
    "minimize removals": OptimizationObjective.MINIMIZE_REMOVALS,
    "min overlapping removal": OptimizationObjective.MINIMIZE_REMOVALS,
    "minimize_resources": OptimizationObjective.MINIMIZE_RESOURCES,
    "minimize resources": OptimizationObjective.MINIMIZE_RESOURCES,
    "min rooms": OptimizationObjective.MINIMIZE_RESOURCES,
    "maximize_concurrency": OptimizationObjective.MAXIMIZE_CONCURRENCY,
    "max concurrency": OptimizationObjective.MAXIMIZE_CONCURRENCY,
    "shortest_path": OptimizationObjective.SHORTEST_PATH,
    "fewest_steps": OptimizationObjective.FEWEST_STEPS,
    "min jumps": OptimizationObjective.FEWEST_STEPS,
    "existence_check": OptimizationObjective.EXISTENCE_CHECK,
    "none": OptimizationObjective.NONE
}


def normalize_representation(raw: str) -> Optional[Representation]:
    """Normalizes raw representation string to controlled enum."""
    clean = re.sub(r"[_\s-]+", "_", raw.strip().lower())
    return REPRESENTATION_ALIASES.get(clean) or REPRESENTATION_ALIASES.get(raw.strip().lower())


def normalize_mechanism(raw: str) -> Optional[Mechanism]:
    """Normalizes raw mechanism string to controlled enum."""
    clean = re.sub(r"[_\s-]+", "_", raw.strip().lower())
    return MECHANISM_ALIASES.get(clean) or MECHANISM_ALIASES.get(raw.strip().lower())


def normalize_objective(raw: str) -> OptimizationObjective:
    """Normalizes raw objective string to controlled enum."""
    clean = re.sub(r"[_\s-]+", "_", raw.strip().lower())
    return OBJECTIVE_ALIASES.get(clean, OptimizationObjective.NONE)


def normalize_concept_id(raw: str) -> str:
    """Normalizes concept tokens into canonical snake_case identifiers."""
    clean = re.sub(r"[^\w\s-]", "", raw).strip().lower()
    return re.sub(r"[-\s]+", "_", clean)
