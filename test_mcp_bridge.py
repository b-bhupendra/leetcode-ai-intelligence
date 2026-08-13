"""
Automated Verification Suite for LeetCode DSA MCP Server & Two-Way Reverse Web Bridge
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from web_app import app
import mcp_server

def test_mcp_and_web_bridge():
    print("=== Testing MCP Server Tools & Reverse Web Bridge ===")

    # -------------------------------------------------------------
    # 1. Test MCP Tool: query_company_radar
    # -------------------------------------------------------------
    print("\n--- Test 1: MCP Tool 'query_company_radar' ---")
    radar = mcp_server.query_company_radar("google", difficulty="Medium", topic="Graph", max_direct=5, max_similar=3)
    assert radar["company"] == "GOOGLE"
    assert len(radar["directly_asked_questions"]) > 0
    assert len(radar["similar_unasked_high_probability_questions"]) > 0
    print(f" [PASS] query_company_radar: Returned {len(radar['directly_asked_questions'])} direct Google problems and {len(radar['similar_unasked_high_probability_questions'])} novel counterparts.")

    # -------------------------------------------------------------
    # 2. Test MCP Tool: get_problem_full_specs
    # -------------------------------------------------------------
    print("\n--- Test 2: MCP Tool 'get_problem_full_specs' ---")
    specs = mcp_server.get_problem_full_specs("trapping-rain-water")
    assert specs["task_id"] == "trapping-rain-water"
    assert len(specs["platform_alternatives"]) == 5
    assert len(specs["similar_counterparts"]) == 5
    print(f" [PASS] get_problem_full_specs: Retrieved specifications and 5 platform links for 'trapping-rain-water'.")

    # -------------------------------------------------------------
    # 3. Test MCP Tool: analyze_candidate_solution
    # -------------------------------------------------------------
    print("\n--- Test 3: MCP Tool 'analyze_candidate_solution' ---")
    code_sample = """
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        lookup = {}
        for i, num in enumerate(nums):
            diff = target - num
            if diff in lookup:
                return [lookup[diff], i]
            lookup[num] = i
        return []
    """
    analysis = mcp_server.analyze_candidate_solution("two-sum", code_sample)
    assert analysis["problem_title"] == "two-sum"
    assert analysis["detected_patterns"]["uses_hashmap"] is True
    assert analysis["detected_patterns"]["uses_loops"] is True
    print(f" [PASS] analyze_candidate_solution: Detected hashmap & loop patterns, cluster '{analysis['cluster_archetype']}'.")

    # -------------------------------------------------------------
    # 4. Test MCP Tool: adaptive_difficulty_stepper
    # -------------------------------------------------------------
    print("\n--- Test 4: MCP Tool 'adaptive_difficulty_stepper' ---")
    # Step down for a struggled student
    step_down = mcp_server.adaptive_difficulty_stepper("course-schedule-ii", performance_rating="struggled", direction="decrease")
    assert len(step_down["recommended_stepped_problems"]) > 0
    print(f" [PASS] adaptive_difficulty_stepper (step-down): {step_down['stepping_intent']} -> Recommended {len(step_down['recommended_stepped_problems'])} foundational problems.")

    # Step up for a mastered student
    step_up = mcp_server.adaptive_difficulty_stepper("two-sum", performance_rating="mastered", direction="increase")
    assert len(step_up["recommended_stepped_problems"]) > 0
    print(f" [PASS] adaptive_difficulty_stepper (step-up): {step_up['stepping_intent']} -> Recommended {len(step_up['recommended_stepped_problems'])} challenge problems.")

    # -------------------------------------------------------------
    # 5. Test MCP Tool: suggest_custom_problem_concept
    # -------------------------------------------------------------
    print("\n--- Test 5: MCP Tool 'suggest_custom_problem_concept' ---")
    concept = mcp_server.suggest_custom_problem_concept("Meta", ["Trie", "Sliding Window"], "Hard")
    assert concept["target_company"] == "META"
    assert "synthesis_prompt" in concept
    print(f" [PASS] suggest_custom_problem_concept: Synthesized custom mock prompt for Meta.")

    # -------------------------------------------------------------
    # 6. Test Reverse MCP Web Broadcast & Web Endpoints
    # -------------------------------------------------------------
    print("\n--- Test 6: Reverse MCP Broadcast & FastAPI SSE Endpoints ---")
    client = TestClient(app)

    # Broadcast an agent action
    r_bc = client.post("/api/agent/broadcast", json={
        "title": "Agent Adaptive Step-Down",
        "action_type": "adaptive_step",
        "content": "Recommended 'find-if-path-exists-in-graph' to master BFS traversal.",
        "problem_slug": "find-if-path-exists-in-graph"
    })
    assert r_bc.status_code == 200
    assert r_bc.json()["status"] == "broadcasted"

    # Query events
    r_ev = client.get("/api/agent/events")
    assert r_ev.status_code == 200
    events = r_ev.json()["events"]
    assert any(e["title"] == "Agent Adaptive Step-Down" for e in events)
    print(f" [PASS] /api/agent/broadcast & /api/agent/events: Event successfully queued and retrievable.")

    # Web-to-Agent trigger endpoint
    r_rev = client.post("/api/agent/analyze-solution", json={
        "problem_slug": "two-sum",
        "candidate_code": code_sample,
        "performance_rating": "mastered"
    })
    assert r_rev.status_code == 200
    rev_data = r_rev.json()["data"]
    assert len(rev_data["recommended_next_problems"]) > 0
    print(f" [PASS] /api/agent/analyze-solution: Computed adaptive follow-up challenges: {[p['task_id'] for p in rev_data['recommended_next_problems']]}")

    print("\n ALL MCP SERVER TOOLS & REVERSE WEB BRIDGE TESTS PASSED!")

if __name__ == "__main__":
    test_mcp_and_web_bridge()
