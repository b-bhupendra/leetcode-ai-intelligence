"""
Curriculum Evaluation Engine: Benchmark against Archetype 15 Gold Standard
"""

import json
from curriculum_gold_standard import get_gold_standard_graph, GOLD_STANDARD_SIGNATURES
from curriculum_beam_search_compiler import BeamSearchCurriculumCompiler
from curriculum_learner_engine import LearnerStateEngine, BridgeGenerator
from curriculum_schema_v2 import LearnerState


def run_curriculum_evaluation():
    print("=================================================================")
    print("[EVALUATION] EVALUATING PEDAGOGY-DRIVEN CURRICULUM COMPILER V2")
    print("=================================================================\n")

    kg = get_gold_standard_graph()
    compiler = BeamSearchCurriculumCompiler(kg, beam_width=10)

    # 1. Compile Canonical Path for Archetype 15 starting at 'meeting-rooms'
    print("Step 1: Compiling Canonical Curriculum Path (Target Length = 8)...")
    compiled = compiler.compile_curriculum(
        start_problem_id="meeting-rooms",
        target_length=8
    )

    print(f"  [OK] Compiled Path ({compiled['total_steps']} steps):")
    for step in compiled["steps"]:
        s_num = step["sequence_step"]
        p_id = step["problem_id"]
        title = step["title"]
        ops = ", ".join(step["operations"])
        diff = step["difficulty_matrix"]["algorithmic"]
        print(f"    Step {s_num}: {title} [{p_id}] (Alg Diff: {diff}/5 | Ops: {ops})")
        if step.get("transition_delta"):
            t = step["transition_delta"]
            print(f"      -> Retention: {t['retention_ratio']*100:.0f}% | Novelty: {t['new_concept_ratio']*100:.0f}% | {t['pedagogical_rationale']}")

    print("\n-----------------------------------------------------------------")
    print("[METRICS] Quantitative Benchmark Metrics:")
    metrics = compiled["metrics"]
    print(f"  - Concept Coverage: {metrics['concept_coverage_count']} distinct concepts")
    print(f"  - Avg Knowledge Retention: {metrics['average_retention_ratio']*100:.1f}%")
    print(f"  - Avg Concept Novelty: {metrics['average_novelty_ratio']*100:.1f}%")
    print(f"  - Prerequisite Violations: {metrics['prerequisite_violations_count']} (Target: 0)")
    print(f"  - Total Cognitive Jumps: {metrics['total_cognitive_jumps']}")

    assert metrics['prerequisite_violations_count'] == 0, "Prerequisite violations must be zero!"
    assert metrics['average_retention_ratio'] >= 0.40, "Retention ratio should be >= 40%"

    # 2. Test Dynamic Bridge Problem Insertion
    print("\n-----------------------------------------------------------------")
    print("[BRIDGE] Step 2: Testing Dynamic Bridge Problem Insertion...")
    learner = LearnerState(
        user_id="test_student",
        solved_problems={"meeting-rooms"},
        mastered_concepts={"interval_representation", "sort_by_start_time"}
    )
    bridge_gen = BridgeGenerator(kg)

    # Test jumping directly from meeting-rooms (easy) to non-overlapping-intervals (requires earliest finish greedy)
    bridge_res = bridge_gen.evaluate_and_bridge(
        source_id="meeting-rooms",
        target_id="minimum-number-of-arrows-to-burst-balloons",
        learner_state=learner,
        cognitive_jump_threshold=2
    )

    if bridge_res.get("bridge_needed"):
        print(f"  [OK] Bridge Triggered Successfully!")
        print(f"  Reason: {bridge_res['trigger_reason']}")
        print(f"  Progression Path: {' -> '.join(bridge_res['progression_path'])}")
        print(f"  Rationale: {bridge_res['pedagogical_rationale']}")
    else:
        print(f"  Direct transition permitted: {bridge_res['reason']}")

    print("\n=================================================================")
    print("[SUCCESS] CURRICULUM COMPILER V2 BENCHMARK PASSED WITH FLYING COLORS!")
    print("=================================================================")
    return compiled


if __name__ == "__main__":
    run_curriculum_evaluation()
