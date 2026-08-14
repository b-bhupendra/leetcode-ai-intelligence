"""
Curriculum Knowledge Graph: DAG of Concepts, Problems, and Prerequisites
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
from curriculum_schema_v2 import ProblemSignature


class KnowledgeGraph:
    """
    Directed Acyclic Graph representing concept prerequisite topology
    and problem skill signature mappings.
    """
    def __init__(self):
        self.problem_signatures: Dict[str, ProblemSignature] = {}
        self.concept_to_problems: Dict[str, List[str]] = defaultdict(list)
        self.concept_prerequisites: Dict[str, Set[str]] = defaultdict(set)
        self.problem_prerequisites: Dict[str, Set[str]] = defaultdict(set)
        self.concept_introduced_by: Dict[str, List[str]] = defaultdict(list)

    def add_problem_signature(self, sig: ProblemSignature):
        """Indexes a validated problem signature into the knowledge graph."""
        self.problem_signatures[sig.problem_id] = sig

        # Index introduced concepts
        for concept in sig.introduced_concepts:
            self.concept_to_problems[concept].append(sig.problem_id)
            self.concept_introduced_by[concept].append(sig.problem_id)

        # Index prerequisite concepts
        for prereq in sig.prerequisite_concepts:
            self.concept_to_problems[prereq].append(sig.problem_id)
            for intro in sig.introduced_concepts:
                self.concept_prerequisites[intro].add(prereq)

    def get_candidate_next_problems(
        self,
        current_id: str,
        visited_ids: Set[str],
        pool_ids: Optional[Set[str]] = None
    ) -> List[ProblemSignature]:
        """
        Retrieves valid pedagogical next candidates from the graph:
        Filters out already visited problems and filters by pool if specified.
        """
        current_sig = self.problem_signatures.get(current_id)
        if not current_sig:
            return []

        candidates = []
        for pid, sig in self.problem_signatures.items():
            if pid in visited_ids:
                continue
            if pool_ids is not None and pid not in pool_ids:
                continue
            candidates.append(sig)

        return candidates

    def find_bridge_candidates(
        self,
        source_id: str,
        target_id: str,
        visited_ids: Set[str]
    ) -> List[ProblemSignature]:
        """
        Searches graph for intermediate bridge problems between source and target:
        Bridge should introduce some missing prerequisites of target while retaining source concepts.
        """
        src = self.problem_signatures.get(source_id)
        tgt = self.problem_signatures.get(target_id)
        if not src or not tgt:
            return []

        src_concepts = set(src.introduced_concepts)
        tgt_prereqs = set(tgt.prerequisite_concepts)
        missing_prereqs = tgt_prereqs - src_concepts

        bridge_scores = []
        for pid, candidate in self.problem_signatures.items():
            if pid == source_id or pid == target_id or pid in visited_ids:
                continue

            cand_intro = set(candidate.introduced_concepts)
            cand_prereqs = set(candidate.prerequisite_concepts)

            # Check if candidate covers any missing prereq
            covered = missing_prereqs.intersection(cand_intro)
            retained_from_src = src_concepts.intersection(cand_prereqs.union(cand_intro))

            # Bridge suitability score
            score = len(covered) * 2.0 + len(retained_from_src) * 1.0
            if score > 0:
                bridge_scores.append((score, candidate))

        bridge_scores.sort(key=lambda x: x[0], reverse=True)
        return [cand for _, cand in bridge_scores]
