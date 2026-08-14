"""
Curriculum Transition Evaluator: Directional Concept Deltas & Multi-Dimensional Jumps
"""

from typing import Dict, List, Set, Any, Optional
from curriculum_schema_v2 import ProblemSignature, TransitionDelta, LearnerState


def compute_transition_delta(
    source: ProblemSignature,
    target: ProblemSignature,
    learner_state: Optional[LearnerState] = None,
    accumulated_path_concepts: Optional[Set[str]] = None
) -> TransitionDelta:
    """
    Computes directional transition vector Δ(A, B) between source and target problems:
    - Retention Ratio: concepts reused from prior knowledge base / target concepts
    - New Concept Ratio: |C_B \ C_Prior| / |C_B|
    - Dropped Concept Ratio: |C_A \ C_B| / |C_A|
    - Cognitive Jumps: max(0, Difficulty_B - Difficulty_A)
    - Prerequisite Satisfaction: Check if all target prerequisites are met
    """
    src_concepts = set(source.introduced_concepts)
    tgt_concepts = set(target.introduced_concepts)
    tgt_prereqs = set(target.prerequisite_concepts)
    mastered = learner_state.mastered_concepts if learner_state else set()

    prior_pool = accumulated_path_concepts if accumulated_path_concepts is not None else src_concepts
    all_known_concepts = prior_pool.union(mastered)

    # 1. Concept Overlap & Retention Metrics
    retained = sorted(list(tgt_prereqs.intersection(all_known_concepts).union(src_concepts.intersection(tgt_concepts))))
    new_concepts = sorted(list(tgt_concepts - all_known_concepts))
    dropped = sorted(list(src_concepts - tgt_concepts))

    retention_ratio = len(retained) / max(len(tgt_prereqs.union(tgt_concepts)), 1) if (tgt_prereqs or tgt_concepts) else 1.0
    new_concept_ratio = len(new_concepts) / max(len(tgt_concepts), 1)
    dropped_concept_ratio = len(dropped) / max(len(src_concepts), 1)

    # 2. Cognitive Difficulty Jumps and Regressions (across 6 dimensions)
    src_diff = source.difficulty_matrix.to_dict()
    tgt_diff = target.difficulty_matrix.to_dict()

    cognitive_jumps = {}
    cognitive_regressions = {}
    for dim in src_diff:
        delta = tgt_diff[dim] - src_diff[dim]
        if delta > 0:
            cognitive_jumps[dim] = delta
            cognitive_regressions[dim] = 0
        else:
            cognitive_jumps[dim] = 0
            cognitive_regressions[dim] = abs(delta)

    # 3. Prerequisite Verification
    # Target prerequisites must be a subset of all known/accumulated concepts
    satisfied_prereqs = tgt_prereqs.issubset(all_known_concepts)

    # 4. Mechanism change summary
    src_ops = [op.value for op in source.operations]
    tgt_ops = [op.value for op in target.operations]
    if src_ops == tgt_ops:
        mechanism_change = f"Preserved ({', '.join(src_ops)})"
    else:
        mechanism_change = f"{', '.join(src_ops)} -> {', '.join(tgt_ops)}"

    # 5. Composite Transition Score:
    # High retention + controlled novelty + low cognitive jump + satisfied prereqs
    total_jump = sum(cognitive_jumps.values())
    prereq_bonus = 1.0 if satisfied_prereqs else -1.5

    # Penalize excessive cognitive jump (>2 in any single dimension or total jump > 4)
    jump_penalty = 0.0
    for dim, jump in cognitive_jumps.items():
        if jump >= 2:
            jump_penalty += 0.8 * jump

    # Optimal transition: retention ~0.5-0.8, novelty ~0.2-0.5
    novelty_fit = 1.0 - abs(new_concept_ratio - 0.35)
    retention_fit = retention_ratio

    transition_score = (
        0.35 * retention_fit +
        0.30 * novelty_fit +
        0.25 * prereq_bonus -
        0.20 * (dropped_concept_ratio * 0.5) -
        0.25 * jump_penalty
    )

    # Generate explainability rationale
    retained_str = ", ".join(retained) if retained else "None"
    introduced_str = ", ".join(new_concepts) if new_concepts else "None"
    rationale = (
        f"Retained: [{retained_str}] | Introduced: [{introduced_str}] | "
        f"Mechanisms: {mechanism_change} | Cognitive Jump: {total_jump}"
    )

    return TransitionDelta(
        source_problem_id=source.problem_id,
        target_problem_id=target.problem_id,
        retention_ratio=round(retention_ratio, 3),
        new_concept_ratio=round(new_concept_ratio, 3),
        dropped_concept_ratio=round(dropped_concept_ratio, 3),
        cognitive_jumps=cognitive_jumps,
        cognitive_regressions=cognitive_regressions,
        retained_concepts=retained,
        introduced_concepts=new_concepts,
        dropped_concepts=dropped,
        mechanism_change=mechanism_change,
        prerequisite_satisfied=satisfied_prereqs,
        total_transition_score=round(transition_score, 3),
        pedagogical_rationale=rationale
    )
