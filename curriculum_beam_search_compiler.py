"""
Curriculum Beam Search Compiler: Global Pedagogical Optimization (K=10)
"""

from typing import List, Dict, Set, Optional, Tuple, Any
from curriculum_schema_v2 import ProblemSignature, TransitionDelta, LearnerState
from curriculum_transition_evaluator import compute_transition_delta
from curriculum_knowledge_graph import KnowledgeGraph


class BeamSearchCurriculumCompiler:
    """
    Pedagogical Curriculum Compiler using Constrained Beam Search.
    Compiles a set of candidate problems into an optimal, coherent learning progression.
    """
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        beam_width: int = 10,
        alpha_gain: float = 0.30,
        beta_retention: float = 0.25,
        gamma_coverage: float = 0.25,
        delta_mastery: float = 0.20,
        lambda_jump_penalty: float = 0.30,
        mu_violation_penalty: float = 0.50,
        rho_redundancy_penalty: float = 0.20
    ):
        self.kg = knowledge_graph
        self.beam_width = beam_width
        self.alpha = alpha_gain
        self.beta = beta_retention
        self.gamma = gamma_coverage
        self.delta = delta_mastery
        self.lambda_jump = lambda_jump_penalty
        self.mu_violation = mu_violation_penalty
        self.rho_redundancy = rho_redundancy_penalty

    def compile_curriculum(
        self,
        start_problem_id: str,
        target_length: int = 8,
        learner_state: Optional[LearnerState] = None,
        candidate_pool: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Compiles an optimal learning sequence from start_problem_id up to target_length
        using Constrained Beam Search over the concept knowledge graph.
        """
        start_sig = self.kg.problem_signatures.get(start_problem_id)
        if not start_sig:
            raise ValueError(f"Start problem '{start_problem_id}' not found in knowledge graph.")

        # Beam state: list of (cumulative_score, path_signatures, transitions)
        # Initial beam with start problem
        initial_path = [start_sig]
        initial_transitions: List[TransitionDelta] = []
        beam: List[Tuple[float, List[ProblemSignature], List[TransitionDelta]]] = [
            (0.0, initial_path, initial_transitions)
        ]

        all_pool = candidate_pool if candidate_pool is not None else set(self.kg.problem_signatures.keys())

        for step in range(1, target_length):
            candidates_expansions = []

            for path_score, current_path, transitions in beam:
                last_sig = current_path[-1]
                visited_ids = {p.problem_id for p in current_path}

                # Find valid unvisited next candidates
                next_candidates = self.kg.get_candidate_next_problems(
                    current_id=last_sig.problem_id,
                    visited_ids=visited_ids,
                    pool_ids=all_pool
                )

                if not next_candidates:
                    # End of graph reached for this path
                    candidates_expansions.append((path_score, current_path, transitions))
                    continue

                path_concepts = {c for p in current_path for c in p.introduced_concepts}
                for candidate in next_candidates:
                    # Compute directional transition delta relative to accumulated concepts
                    delta = compute_transition_delta(
                        source=last_sig,
                        target=candidate,
                        learner_state=learner_state,
                        accumulated_path_concepts=path_concepts
                    )

                    # Compute step pedagogical score
                    step_score = self._score_step(
                        source=last_sig,
                        target=candidate,
                        delta=delta,
                        current_path=current_path,
                        learner_state=learner_state
                    )

                    new_path_score = path_score + step_score
                    new_path = current_path + [candidate]
                    new_transitions = transitions + [delta]

                    candidates_expansions.append((new_path_score, new_path, new_transitions))

            if not candidates_expansions:
                break

            # Sort expansions by score descending and prune to top-K
            candidates_expansions.sort(key=lambda x: x[0], reverse=True)
            beam = candidates_expansions[:self.beam_width]

        # Best compiled path
        best_score, best_path, best_transitions = beam[0]

        # Calculate overall curriculum metrics
        all_introduced_concepts = set()
        for p in best_path:
            all_introduced_concepts.update(p.introduced_concepts)

        avg_retention = sum(t.retention_ratio for t in best_transitions) / max(len(best_transitions), 1)
        avg_novelty = sum(t.new_concept_ratio for t in best_transitions) / max(len(best_transitions), 1)
        total_cognitive_jumps = sum(sum(t.cognitive_jumps.values()) for t in best_transitions)
        prereq_violations = sum(1 for t in best_transitions if not t.prerequisite_satisfied)

        # Build steps payload with full explainability contract
        compiled_steps = []
        for i, p in enumerate(best_path):
            trans = best_transitions[i-1] if i > 0 else None
            trans_dict = None
            if trans:
                trans_dict = trans.model_dump()
                # Flatten learner-friendly keys to top level of transition_delta
                trans_dict['retained_concepts'] = trans.retained_concepts
                trans_dict['new_concepts'] = trans.introduced_concepts
                trans_dict['mechanism_change_summary'] = trans.mechanism_change

            compiled_steps.append({
                "sequence_step": i + 1,
                "problem_id": p.problem_id,
                "title": p.title or p.problem_id.replace("-", " ").title(),
                "canonical_pattern": p.canonical_pattern,
                "difficulty_matrix": p.difficulty_matrix.to_dict(),
                "introduced_concepts": p.introduced_concepts,
                "prerequisite_concepts": p.prerequisite_concepts,
                "operations": [op.value for op in p.operations],
                "transition_delta": trans_dict,
                "pedagogical_reason": trans.pedagogical_rationale if trans else "Initial baseline problem"
            })

        return {
            "status": "success",
            "curriculum_path_id": f"path_{start_problem_id}_{target_length}",
            "start_problem": start_problem_id,
            "total_steps": len(best_path),
            "global_pedagogical_score": round(best_score, 3),
            "metrics": {
                "concept_coverage_count": len(all_introduced_concepts),
                "average_retention_ratio": round(avg_retention, 3),
                "average_novelty_ratio": round(avg_novelty, 3),
                "total_cognitive_jumps": total_cognitive_jumps,
                "prerequisite_violations_count": prereq_violations,
                "beam_width_evaluated": self.beam_width
            },
            "steps": compiled_steps
        }

    def _score_step(
        self,
        source: ProblemSignature,
        target: ProblemSignature,
        delta: TransitionDelta,
        current_path: List[ProblemSignature],
        learner_state: Optional[LearnerState]
    ) -> float:
        """
        Global pedagogical step scoring function:
        Score = α*Gain + β*Retention + γ*Coverage + δ*Mastery - λ*Jump - μ*Violation - ρ*Redundancy
        """
        # G: Learning Gain (controlled novelty)
        gain = delta.new_concept_ratio

        # R: Retention
        retention = delta.retention_ratio

        # C: Coverage bonus (introduces concepts not yet seen in current path)
        path_concepts = {c for p in current_path for c in p.introduced_concepts}
        new_unique = set(target.introduced_concepts) - path_concepts
        coverage = len(new_unique) * 0.25

        # M: Learner Mastery Alignment
        mastery = 0.0
        if learner_state:
            # If target concepts build on mastered concepts
            mastered = learner_state.mastered_concepts
            overlap = set(target.prerequisite_concepts).intersection(mastered)
            mastery = len(overlap) * 0.2

        # J: Cognitive Jumps Penalty
        jump_sum = sum(delta.cognitive_jumps.values())
        jump_penalty = jump_sum * 0.15

        # V: Prerequisite Violations Penalty
        violation_penalty = 0.0 if delta.prerequisite_satisfied else 1.0

        # D: Redundancy Penalty (exact duplicate concepts and mechanisms)
        redundancy_penalty = 0.0
        if delta.new_concept_ratio == 0.0 and delta.retention_ratio == 1.0:
            redundancy_penalty = 0.8

        step_score = (
            self.alpha * gain +
            self.beta * retention +
            self.gamma * coverage +
            self.delta * mastery -
            self.lambda_jump * jump_penalty -
            self.mu_violation * violation_penalty -
            self.rho_redundancy * redundancy_penalty
        )
        return step_score
