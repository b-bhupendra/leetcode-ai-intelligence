"""
Curriculum Gold Standard: 30 Curated Problem Signatures for Archetype 15
(Interval Scheduling, Sweep-Line & Greedy Choice)
"""

from typing import List, Dict
from curriculum_schema_v2 import (
    ProblemSignature, DifficultyMatrix, Representation,
    Mechanism, OptimizationObjective, SignatureMetadata, ExtractionEvidence
)

GOLD_STANDARD_SIGNATURES: List[ProblemSignature] = [
    # 1. Meeting Rooms (252) - Foundational Interval Overlap Detection
    ProblemSignature(
        problem_id="meeting-rooms",
        title="Meeting Rooms",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.SORT_START],
        decision_rules=["check_overlap_intervals[i][1] > intervals[i+1][0]"],
        invariants=["sorted by start time: start[i] <= start[i+1]"],
        optimization_objective=OptimizationObjective.EXISTENCE_CHECK,
        introduced_concepts=["interval_representation", "sort_by_start_time", "adjacent_overlap_check"],
        prerequisite_concepts=[],
        hidden_assumptions=["end time <= next start time indicates no conflict"],
        common_traps=["forgetting to sort before linear check"],
        difficulty_matrix=DifficultyMatrix(algorithmic=1, implementation=1, reasoning=1, state_complexity=1, edge_cases=2, cognitive_load=1)
    ),

    # 2. Merge Intervals (56) - In-place/Accumulator Interval Merging
    ProblemSignature(
        problem_id="merge-intervals",
        title="Merge Intervals",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.SORT_START, Mechanism.GREEDY_SELECTION],
        decision_rules=["if curr[0] <= prev[1] then merge prev[1] = max(prev[1], curr[1]) else append"],
        invariants=["all merged intervals up to i are mutually disjoint"],
        optimization_objective=OptimizationObjective.NONE,
        introduced_concepts=["interval_merging", "running_interval_accumulator", "max_endpoint_extension"],
        prerequisite_concepts=["interval_representation", "sort_by_start_time", "adjacent_overlap_check"],
        hidden_assumptions=["input can be mutated or collected into a new list"],
        common_traps=["assuming intervals are pre-sorted"],
        difficulty_matrix=DifficultyMatrix(algorithmic=2, implementation=2, reasoning=2, state_complexity=2, edge_cases=2, cognitive_load=2)
    ),

    # 3. Insert Interval (57) - Linear Three-Phase Binary/Linear Sweep
    ProblemSignature(
        problem_id="insert-interval",
        title="Insert Interval",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.GREEDY_SELECTION],
        decision_rules=["three phases: strictly before, overlapping merge, strictly after"],
        invariants=["input is already sorted and non-overlapping"],
        optimization_objective=OptimizationObjective.NONE,
        introduced_concepts=["three_phase_interval_partition", "sorted_insertion_without_full_resort"],
        prerequisite_concepts=["interval_representation", "interval_merging"],
        hidden_assumptions=["intervals are already sorted by start and disjoint"],
        common_traps=["merging when newInterval is completely before or after all others"],
        difficulty_matrix=DifficultyMatrix(algorithmic=2, implementation=3, reasoning=2, state_complexity=2, edge_cases=3, cognitive_load=2)
    ),

    # 4. Non-overlapping Intervals (435) - Earliest Finish Time Greedy
    ProblemSignature(
        problem_id="non-overlapping-intervals",
        title="Non-overlapping Intervals",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.SORT_END, Mechanism.GREEDY_SELECTION],
        decision_rules=["sort by end time; if overlap detected, drop interval with larger end time"],
        invariants=["earliest finish time leaves maximal remaining space for future intervals"],
        optimization_objective=OptimizationObjective.MINIMIZE_REMOVALS,
        introduced_concepts=["earliest_finish_time_greedy", "interval_removal_minimization"],
        prerequisite_concepts=["interval_representation", "adjacent_overlap_check"],
        hidden_assumptions=["sorting by start time is sub-optimal for interval selection"],
        common_traps=["sorting by start time instead of end time"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=2, reasoning=3, state_complexity=2, edge_cases=2, cognitive_load=3)
    ),

    # 5. Minimum Number of Arrows to Burst Balloons (452) - Range Intersection Greedy
    ProblemSignature(
        problem_id="minimum-number-of-arrows-to-burst-balloons",
        title="Minimum Number of Arrows to Burst Balloons",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.SORT_END, Mechanism.GREEDY_SELECTION],
        decision_rules=["if curr[0] > prev_arrow_pos: shoot new arrow at curr[1]"],
        invariants=["arrow placed at minimal end point bursts maximal contiguous overlaps"],
        optimization_objective=OptimizationObjective.MINIMIZE_RESOURCES,
        introduced_concepts=["greedy_arrow_placement", "point_stabbing_interval_set"],
        prerequisite_concepts=["interval_representation", "earliest_finish_time_greedy"],
        hidden_assumptions=["32-bit signed integer subtraction can overflow in sort comparator"],
        common_traps=["using a - b comparator instead of Integer.compare"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=2, reasoning=3, state_complexity=2, edge_cases=3, cognitive_load=3)
    ),

    # 6. Meeting Rooms II (253) - Multi-Resource Allocation with Min-Heap
    ProblemSignature(
        problem_id="meeting-rooms-ii",
        title="Meeting Rooms II",
        canonical_pattern="greedy_interval_scheduling",
        representations=[Representation.INTERVAL_1D, Representation.HEAP_TREE],
        data_structures=["array_1d", "min_heap"],
        operations=[Mechanism.SORT_START, Mechanism.MIN_HEAP],
        decision_rules=["heap stores earliest available room end times; if curr[0] >= heap.top() reuse room"],
        invariants=["heap size at any moment represents active concurrent rooms"],
        optimization_objective=OptimizationObjective.MINIMIZE_RESOURCES,
        introduced_concepts=["min_heap_resource_tracking", "dynamic_concurrency_tracking"],
        prerequisite_concepts=["interval_representation", "sort_by_start_time"],
        hidden_assumptions=["a room freed at time t can be used immediately at time t"],
        common_traps=["popping from heap unconditionally"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=3, reasoning=3, state_complexity=3, edge_cases=2, cognitive_load=3)
    ),

    # 7. Car Pooling (1094) - Sweep-Line / Difference Array on Timestamps
    ProblemSignature(
        problem_id="car-pooling",
        title="Car Pooling",
        canonical_pattern="sweep_line_difference_array",
        representations=[Representation.ARRAY_1D, Representation.INTERVAL_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.SWEEP_LINE, Mechanism.PREFIX_SUM],
        decision_rules=["diff[start] += passengers; diff[end] -= passengers; check prefix sum <= capacity"],
        invariants=["running sum at point t equals exact passenger count at mile t"],
        optimization_objective=OptimizationObjective.EXISTENCE_CHECK,
        introduced_concepts=["difference_array_sweep_line", "event_point_delta_accumulation"],
        prerequisite_concepts=["adjacent_overlap_check", "prefix_sum"],
        hidden_assumptions=["passengers drop off before new ones board at the same location"],
        common_traps=["treating end location as inclusive passenger load"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=2, reasoning=3, state_complexity=2, edge_cases=2, cognitive_load=3)
    ),

    # 8. My Calendar I (729) - Online Dynamic Interval Insertion (BST / TreeMap)
    ProblemSignature(
        problem_id="my-calendar-i",
        title="My Calendar I",
        canonical_pattern="dynamic_interval_search",
        representations=[Representation.INTERVAL_1D, Representation.TREE_BINARY],
        data_structures=["binary_search_tree"],
        operations=[Mechanism.BINARY_SEARCH],
        decision_rules=["find floor and ceiling intervals; verify no overlap with adjacent booked intervals"],
        invariants=["BST keeps intervals sorted dynamically with O(log N) lookup"],
        optimization_objective=OptimizationObjective.EXISTENCE_CHECK,
        introduced_concepts=["online_interval_insertion", "bst_floor_ceiling_lookup"],
        prerequisite_concepts=["interval_representation", "adjacent_overlap_check"],
        hidden_assumptions=["intervals are half-open [start, end)"],
        common_traps=["checking only floor and forgetting ceiling"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=3, reasoning=3, state_complexity=3, edge_cases=3, cognitive_load=3)
    ),

    # 9. My Calendar III (732) - Maximum K-Concurrent Booking (Coordinate Sweep)
    ProblemSignature(
        problem_id="my-calendar-iii",
        title="My Calendar III",
        canonical_pattern="sweep_line_difference_array",
        representations=[Representation.ARRAY_1D],
        data_structures=["treemap"],
        operations=[Mechanism.SWEEP_LINE, Mechanism.PREFIX_SUM],
        decision_rules=["delta[start] += 1; delta[end] -= 1; max_k = max(running_sum)"],
        invariants=["ordered sweep across all timestamps yields maximal concurrent overlap k"],
        optimization_objective=OptimizationObjective.MAXIMIZE_CONCURRENCY,
        introduced_concepts=["continuous_coordinate_sweep", "online_k_concurrency_maxima"],
        prerequisite_concepts=["difference_array_sweep_line", "online_interval_insertion"],
        hidden_assumptions=["all past bookings persist"],
        common_traps=["resetting delta map between book calls"],
        difficulty_matrix=DifficultyMatrix(algorithmic=4, implementation=3, reasoning=4, state_complexity=3, edge_cases=2, cognitive_load=4)
    ),

    # 10. Jump Game (55) - Max Reachable Index Greedy Frontier
    ProblemSignature(
        problem_id="jump-game",
        title="Jump Game",
        canonical_pattern="greedy_frontier_expansion",
        representations=[Representation.ARRAY_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.GREEDY_SELECTION],
        decision_rules=["max_reach = max(max_reach, i + nums[i]); if i > max_reach return False"],
        invariants=["max_reach always covers all reachable indices discovered so far"],
        optimization_objective=OptimizationObjective.EXISTENCE_CHECK,
        introduced_concepts=["greedy_reachability_frontier", "implicit_interval_expansion"],
        prerequisite_concepts=["array_1d"],
        hidden_assumptions=["indices beyond max_reach are strictly unreachable"],
        common_traps=["trying DP O(N^2) when greedy O(N) is sufficient"],
        difficulty_matrix=DifficultyMatrix(algorithmic=2, implementation=1, reasoning=3, state_complexity=1, edge_cases=2, cognitive_load=2)
    ),

    # 11. Jump Game II (45) - Breadth BFS Level Jump Optimization
    ProblemSignature(
        problem_id="jump-game-ii",
        title="Jump Game II",
        canonical_pattern="greedy_frontier_expansion",
        representations=[Representation.ARRAY_1D],
        data_structures=["array_1d"],
        operations=[Mechanism.GREEDY_SELECTION, Mechanism.BFS_QUEUE],
        decision_rules=["when i reaches current_jump_end: jumps++, current_jump_end = farthest_reach"],
        invariants=["each jump boundary defines the next BFS layer of reachable indices"],
        optimization_objective=OptimizationObjective.FEWEST_STEPS,
        introduced_concepts=["implicit_bfs_level_partition", "minimum_step_frontier_jump"],
        prerequisite_concepts=["greedy_reachability_frontier"],
        hidden_assumptions=["target is always reachable"],
        common_traps=["incrementing jumps on the last element"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=2, reasoning=3, state_complexity=2, edge_cases=2, cognitive_load=3)
    ),

    # 12. Task Scheduler (621) - Frequency Fill & Idle Slot Greedy Math
    ProblemSignature(
        problem_id="task-scheduler",
        title="Task Scheduler",
        canonical_pattern="greedy_frequency_slot_filling",
        representations=[Representation.ARRAY_1D, Representation.HASH_TABLE],
        data_structures=["array_1d", "max_heap"],
        operations=[Mechanism.GREEDY_SELECTION, Mechanism.MAX_HEAP],
        decision_rules=["max_freq tasks determine frame structure: (max_freq - 1) * (n + 1) + count(max_freq_tasks)"],
        invariants=["highest frequency elements dictate the minimum possible idle intervals"],
        optimization_objective=OptimizationObjective.FEWEST_STEPS,
        introduced_concepts=["cooling_period_slot_partition", "frequency_dominant_frame_math"],
        prerequisite_concepts=["dynamic_concurrency_tracking"],
        hidden_assumptions=["if total tasks > calculated frame, answer is simply len(tasks)"],
        common_traps=["simulating cycle-by-cycle when mathematical formula exists"],
        difficulty_matrix=DifficultyMatrix(algorithmic=3, implementation=3, reasoning=4, state_complexity=2, edge_cases=3, cognitive_load=4)
    )
]


def get_gold_standard_graph():
    """Initializes KnowledgeGraph populated with all Gold Standard problem signatures."""
    from curriculum_knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    for sig in GOLD_STANDARD_SIGNATURES:
        kg.add_problem_signature(sig)
    return kg
