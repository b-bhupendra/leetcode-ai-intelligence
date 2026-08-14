"""
Curriculum Learner Engine & Dynamic Bridge Insertion Engine
"""

from typing import Dict, List, Set, Optional, Any
from curriculum_schema_v2 import ProblemSignature, TransitionDelta, LearnerState
from curriculum_transition_evaluator import compute_transition_delta
from curriculum_knowledge_graph import KnowledgeGraph


class LearnerStateEngine:
    """
    Tracks learner submission history, updates mastered concept sets,
    and dynamically estimates multidimensional cognitive capacity.
    """
    def __init__(self, learner_state: Optional[LearnerState] = None):
        self.state = learner_state or LearnerState()

    def record_attempt(
        self,
        problem: ProblemSignature,
        success: bool,
        hints_used: int = 0,
        time_spent_mins: float = 15.0
    ):
        """Records a user attempt and updates mastered concepts and cognitive capacity."""
        pid = problem.problem_id
        entry = {
            "problem_id": pid,
            "success": success,
            "hints_used": hints_used,
            "time_spent_mins": time_spent_mins
        }
        self.state.recent_attempts_history.append(entry)

        if success:
            self.state.solved_problems.add(pid)
            self.state.failed_problems.discard(pid)
            # Add introduced concepts to mastered set
            self.state.mastered_concepts.update(problem.introduced_concepts)

            # Gradually increase cognitive capacity based on problem difficulty
            for dim, val in problem.difficulty_matrix.to_dict().items():
                curr = self.state.current_cognitive_capacity.get(dim, 2)
                if val >= curr:
                    self.state.current_cognitive_capacity[dim] = min(5, curr + 1)
        else:
            self.state.failed_problems.add(pid)

    def get_recent_consecutive_failures(self, problem_id: str) -> int:
        """Counts recent failures on a given problem or concept family."""
        count = 0
        for entry in reversed(self.state.recent_attempts_history):
            if entry.get("problem_id") == problem_id:
                if not entry.get("success"):
                    count += 1
                else:
                    break
        return count


class BridgeGenerator:
    """
    Dynamically generates intermediate bridge problems between source and target
    when cognitive jumps exceed learner capacity or repeated failures occur.
    """
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    def evaluate_and_bridge(
        self,
        source_id: str,
        target_id: str,
        learner_state: LearnerState,
        cognitive_jump_threshold: int = 2
    ) -> Dict[str, Any]:
        """
        Evaluates the transition from source to target.
        If the cognitive jump is too large or target prerequisites are missing,
        searches the knowledge graph and inserts an optimal bridge problem.
        """
        source = self.kg.problem_signatures.get(source_id)
        target = self.kg.problem_signatures.get(target_id)
        if not source or not target:
            raise ValueError("Source or target problem not found in knowledge graph.")

        delta = compute_transition_delta(source, target, learner_state)

        # Check if cognitive jump exceeds threshold in any dimension
        max_jump = max(delta.cognitive_jumps.values()) if delta.cognitive_jumps else 0
        needs_bridge = (
            max_jump >= cognitive_jump_threshold or
            not delta.prerequisite_satisfied or
            target_id in learner_state.failed_problems
        )

        if not needs_bridge:
            return {
                "bridge_needed": False,
                "reason": "Transition is pedagogically smooth and matches learner capacity.",
                "direct_transition": delta.model_dump(),
                "next_problem": target.problem_id
            }

        # Search for candidate bridge problems
        visited = set(learner_state.solved_problems).union({source_id, target_id})
        bridge_candidates = self.kg.find_bridge_candidates(source_id, target_id, visited)

        if not bridge_candidates:
            return {
                "bridge_needed": False,
                "reason": "No intermediate bridge found in pool; proceed with cautionary hint.",
                "direct_transition": delta.model_dump(),
                "next_problem": target.problem_id
            }

        # Pick best bridge problem: highest transition score from source + lowest jump to target
        best_bridge = None
        best_composite = -999.0
        best_delta_to_bridge = None
        best_delta_to_target = None

        for cand in bridge_candidates:
            d1 = compute_transition_delta(source, cand, learner_state)
            d2 = compute_transition_delta(cand, target, learner_state)

            composite = d1.total_transition_score + d2.total_transition_score
            if composite > best_composite:
                best_composite = composite
                best_bridge = cand
                best_delta_to_bridge = d1
                best_delta_to_target = d2

        return {
            "bridge_needed": True,
            "trigger_reason": f"Cognitive jump ({max_jump}) exceeds threshold or prerequisites were unfulfilled.",
            "bridge_problem": {
                "problem_id": best_bridge.problem_id,
                "title": best_bridge.title,
                "canonical_pattern": best_bridge.canonical_pattern,
                "difficulty_matrix": best_bridge.difficulty_matrix.to_dict(),
                "introduced_concepts": best_bridge.introduced_concepts
            },
            "progression_path": [source.problem_id, best_bridge.problem_id, target.problem_id],
            "source_to_bridge_delta": best_delta_to_bridge.model_dump(),
            "bridge_to_target_delta": best_delta_to_target.model_dump(),
            "pedagogical_rationale": (
                f"Bridging {source.problem_id} -> {best_bridge.problem_id} -> {target.problem_id}: "
                f"Introduces intermediate concept [{', '.join(best_bridge.introduced_concepts)}] "
                f"to scaffold knowledge before reaching {target.problem_id}."
            )
        }
