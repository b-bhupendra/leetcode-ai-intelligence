"""
Curriculum Schema V2: Pydantic Data Models & Controlled Schemas
for Pedagogy-Driven Curriculum Compilation & Skill Signatures
"""

from enum import Enum
from typing import List, Dict, Optional, Set, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo


# ==============================================================================
# Controlled Ontology Enums
# ==============================================================================

class Representation(str, Enum):
    ARRAY_1D = "array_1d"
    ARRAY_2D = "array_2d"
    INTERVAL_1D = "interval_1d"
    GRAPH_ADJACENCY = "graph_adjacency"
    TREE_BINARY = "tree_binary"
    STATE_BITMASK = "state_bitmask"
    STRING_TOKENS = "string_tokens"
    LINKED_LIST = "linked_list"
    HEAP_TREE = "heap_tree"
    HASH_TABLE = "hash_table"


class Mechanism(str, Enum):
    SORT_START = "sort_start"
    SORT_END = "sort_end"
    TWO_POINTER_CONVERGE = "two_pointer_converge"
    SLIDING_WINDOW = "sliding_window"
    GREEDY_SELECTION = "greedy_selection"
    MIN_HEAP = "min_heap"
    MAX_HEAP = "max_heap"
    SWEEP_LINE = "sweep_line"
    MONOTONIC_STACK = "monotonic_stack"
    DP_TABULATION = "dp_tabulation"
    DP_MEMOIZATION = "dp_memoization"
    DFS_RECURSION = "dfs_recursion"
    BFS_QUEUE = "bfs_queue"
    BINARY_SEARCH = "binary_search"
    PREFIX_SUM = "prefix_sum"
    UNION_FIND = "union_find"


class OptimizationObjective(str, Enum):
    MAXIMIZE_COUNT = "maximize_count"
    MINIMIZE_REMOVALS = "minimize_removals"
    MINIMIZE_RESOURCES = "minimize_resources"
    MAXIMIZE_CONCURRENCY = "maximize_concurrency"
    SHORTEST_PATH = "shortest_path"
    FEWEST_STEPS = "fewest_steps"
    EXISTENCE_CHECK = "existence_check"
    MAXIMIZE_VALUE = "maximize_value"
    MINIMIZE_COST = "minimize_cost"
    NONE = "none"


# ==============================================================================
# Multi-Dimensional Difficulty Matrix & Evidence
# ==============================================================================

class DifficultyMatrix(BaseModel):
    algorithmic: int = Field(..., ge=1, le=5, description="Complexity of the core algorithm/invariant")
    implementation: int = Field(..., ge=1, le=5, description="Code structure and pointer/index manipulation")
    reasoning: int = Field(..., ge=1, le=5, description="Mathematical/proof leap required to see the greedy/DP choice")
    state_complexity: int = Field(..., ge=1, le=5, description="Number of concurrent variables/bounds tracked")
    edge_cases: int = Field(..., ge=1, le=5, description="Sensitivity to duplicates, bounds, empty inputs")
    cognitive_load: int = Field(..., ge=1, le=5, description="Total working memory required")

    def to_dict(self) -> Dict[str, int]:
        return {
            "algorithmic": self.algorithmic,
            "implementation": self.implementation,
            "reasoning": self.reasoning,
            "state_complexity": self.state_complexity,
            "edge_cases": self.edge_cases,
            "cognitive_load": self.cognitive_load
        }


class ExtractionEvidence(BaseModel):
    field: str = Field(..., description="Target field in signature")
    value: str = Field(..., description="Extracted value")
    reason: str = Field(..., description="Direct quote or constraint justifying selection")


class SignatureMetadata(BaseModel):
    signature_version: str = "2.0.0"
    ontology_version: str = "2.0.0"
    extractor_model: str = "gpt-4o-mini-calibrated"
    confidence_score: float = Field(default=0.92, ge=0.0, le=1.0)
    review_status: str = "validated"  # 'pending_auto', 'validated', 'flagged'


# ==============================================================================
# Problem Skill Signature Schema
# ==============================================================================

class ProblemSignature(BaseModel):
    problem_id: str
    title: str = ""
    canonical_pattern: str
    variant_of: List[str] = Field(default_factory=list)

    # Controlled Attributes
    representations: List[Representation]
    data_structures: List[str]
    operations: List[Mechanism]
    decision_rules: List[str]
    invariants: List[str]
    optimization_objective: OptimizationObjective = OptimizationObjective.NONE

    # Knowledge Graph Edges
    introduced_concepts: List[str]
    prerequisite_concepts: List[str]

    # Context & Traps
    hidden_assumptions: List[str] = Field(default_factory=list)
    common_traps: List[str] = Field(default_factory=list)

    difficulty_matrix: DifficultyMatrix
    extraction_evidence: List[ExtractionEvidence] = Field(default_factory=list)
    meta: SignatureMetadata = Field(default_factory=SignatureMetadata)

    @field_validator("prerequisite_concepts")
    @classmethod
    def validate_no_overlap_with_introduced(cls, v: List[str], info: ValidationInfo):
        introduced = info.data.get("introduced_concepts", []) if info.data else []
        overlap = set(v) & set(introduced)
        if overlap:
            raise ValueError(f"Concepts cannot be both prerequisite and introduced: {overlap}")
        return v


# ==============================================================================
# Transition Delta & Learner State Schemas
# ==============================================================================

class TransitionDelta(BaseModel):
    source_problem_id: str
    target_problem_id: str

    retention_ratio: float = Field(..., ge=0.0, le=1.0)
    new_concept_ratio: float = Field(..., ge=0.0, le=1.0)
    dropped_concept_ratio: float = Field(..., ge=0.0, le=1.0)

    cognitive_jumps: Dict[str, int]
    cognitive_regressions: Dict[str, int]

    retained_concepts: List[str] = Field(default_factory=list)
    introduced_concepts: List[str] = Field(default_factory=list)
    dropped_concepts: List[str] = Field(default_factory=list)
    mechanism_change: str = ""

    prerequisite_satisfied: bool
    total_transition_score: float
    pedagogical_rationale: str = ""


class LearnerState(BaseModel):
    user_id: str = "default_learner"
    solved_problems: Set[str] = Field(default_factory=set)
    failed_problems: Set[str] = Field(default_factory=set)
    mastered_concepts: Set[str] = Field(default_factory=set)

    recent_attempts_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_cognitive_capacity: Dict[str, int] = Field(
        default_factory=lambda: {
            "algorithmic": 2,
            "implementation": 2,
            "reasoning": 2,
            "state_complexity": 2,
            "edge_cases": 2,
            "cognitive_load": 2
        }
    )
