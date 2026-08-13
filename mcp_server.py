"""
LeetCode & DSA Intelligence MCP Server

Exposes grounding tools for LLMs (Antigravity, Claude, Cursor, Gemini):
1. query_company_radar: Grounded company interview question lookup + novel recommendations.
2. analyze_candidate_solution: Code complexity, correctness, edge-case traps, and optimization hints.
3. adaptive_difficulty_stepper: Clustered micro-stepping (step-up / step-down difficulty navigation).
4. suggest_custom_problem_concept: Synthesizes novel problem archetypes tailored to company profiles.
5. push_to_web_dashboard: Reverse MCP bridge that broadcasts actions to the local web host (http://localhost:8000).
6. get_problem_full_specs: Retrieves complete problem statements, starter codes, and test suites.
"""

import os
import json
import urllib.request
import pandas as pd
from typing import Dict, Any, List, Optional
from mcp.server.mcpserver import MCPServer

from ml_models import LeetCodeIntelligenceEngine
from scraper_engine import CrossPlatformMapper

# Initialize MCP Server
mcp = MCPServer("LeetCode-DSA-Intelligence")

# Initialize and load ML Engine
engine = LeetCodeIntelligenceEngine()
engine.load_models()

LOCAL_WEB_BROADCAST_URL = "http://127.0.0.1:8000/api/agent/broadcast"


@mcp.tool()
def query_company_radar(
    company: str,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    timeframe: Optional[str] = "alltime",
    max_direct: int = 10,
    max_similar: int = 5
) -> Dict[str, Any]:
    """
    Retrieves verified interview questions asked by a target tech company (e.g. google, amazon, meta)
    along with 'Similar High-Probability Questions' that match the company's problem archetypes,
    complete with 5 cross-platform alternatives (LeetCode, GFG, LintCode, HackerRank, CodeStudio).
    """
    res = engine.filter_and_recommend(
        company=company,
        difficulty=difficulty,
        topic=topic,
        timeframe=timeframe,
        max_direct=max_direct,
        max_similar=max_similar
    )
    return {
        "company": company.upper(),
        "total_direct_in_dataset": res["direct_count"],
        "directly_asked_questions": res["direct_problems"],
        "similar_unasked_high_probability_questions": res["similar_unasked_problems"]
    }


@mcp.tool()
def get_problem_full_specs(problem_slug_or_id: str) -> Dict[str, Any]:
    """
    Retrieves full specifications, topic tags, difficulty, 5 cross-platform alternatives,
    starter code, canonical solutions, and test suites for any LeetCode problem.
    """
    p = engine.get_problem_by_id_or_slug(str(problem_slug_or_id))
    if not p:
        return {"status": "not_found", "message": f"Problem '{problem_slug_or_id}' not found in database."}
    return p


@mcp.tool()
def analyze_candidate_solution(
    problem_slug_or_id: str,
    candidate_code: str,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Evaluates a candidate's code submission for a DSA problem.
    Provides canonical reference, time/space complexity analysis, edge-case traps,
    and adaptive difficulty recommendations.
    """
    p = engine.get_problem_by_id_or_slug(str(problem_slug_or_id))
    if not p:
        return {"status": "not_found", "message": f"Problem '{problem_slug_or_id}' not found in database."}

    # Extract problem constraints & reference
    canonical = p.get("completion") or p.get("starter_code") or ""
    tags = p.get("topic_tags", [])
    diff = p.get("difficulty", "Medium")
    cluster = p.get("cluster_title", "General")

    # Static heuristic code checks
    code_lower = candidate_code.lower()
    has_recursion = "def " in candidate_code and any(f in candidate_code for f in ["return self.", "solve(", "dfs(", "helper("])
    has_loops = "for " in code_lower or "while " in code_lower
    has_memo = "memo" in code_lower or "dp" in code_lower or "@lru_cache" in code_lower or "@cache" in code_lower
    has_hashmap = "dict(" in code_lower or "{}" in code_lower or "defaultdict" in code_lower or "counter" in code_lower

    analysis = {
        "problem_title": p["task_id"],
        "difficulty": diff,
        "cluster_archetype": cluster,
        "detected_patterns": {
            "uses_recursion": has_recursion,
            "uses_loops": has_loops,
            "uses_memoization_or_dp": has_memo,
            "uses_hashmap": has_hashmap
        },
        "target_companies": p.get("top_companies", [])[:5],
        "cross_platform_alternatives": p.get("platform_alternatives", [])[:3],
        "canonical_reference_available": bool(canonical),
        "guidance_for_llm": (
            f"Compare candidate solution against archetype '{cluster}'. "
            f"Evaluate time/space complexity against standard optimal bounds. "
            f"If suboptimal or failing edge cases, suggest adaptive micro-stepping."
        )
    }
    return analysis


@mcp.tool()
def adaptive_difficulty_stepper(
    current_problem_slug: str,
    performance_rating: str = "struggled",
    direction: str = "decrease"
) -> Dict[str, Any]:
    """
    Navigates the 30 algorithmic archetypes to recommend a step-up or step-down problem.
    - If direction == 'decrease' (or rating == 'struggled'): Recommends a foundational sub-problem from the same cluster.
    - If direction == 'increase' (or rating == 'mastered'): Recommends a harder follow-up variation from the same cluster.
    """
    p = engine.get_problem_by_id_or_slug(current_problem_slug)
    if not p:
        return {"status": "not_found", "message": f"Problem '{current_problem_slug}' not found."}

    curr_diff = p.get("difficulty", "Medium")
    cluster_title = p.get("cluster_title", "General")

    # Determine target difficulty for stepping
    if direction == "decrease" or performance_rating in ["struggled", "poor"]:
        target_diff = "Easy" if curr_diff in ["Medium", "Hard"] else "Easy"
        step_intent = f"Step-Down foundational practice for {cluster_title}"
    else:
        target_diff = "Hard" if curr_diff in ["Medium", "Hard"] else "Medium"
        step_intent = f"Step-Up follow-up challenge for {cluster_title}"

    # Query matching problems within the same cluster archetype
    cluster_probs = engine.df[
        (engine.df["cluster_title"] == cluster_title) &
        (engine.df["difficulty"] == target_diff) &
        (engine.df["task_id"] != current_problem_slug)
    ]

    if len(cluster_probs) == 0:
        # Fallback to similar problems
        similar = p.get("similar_counterparts", [])
        recommendations = similar[:3]
    else:
        recommendations = []
        for _, row in cluster_probs.head(3).iterrows():
            task_id = str(row["task_id"])
            recommendations.append({
                "question_id": int(row["question_id"]) if row.get("question_id") else None,
                "task_id": task_id,
                "difficulty": row["difficulty"],
                "cluster_title": cluster_title,
                "topic_tags": row["topic_tags"] if isinstance(row["topic_tags"], list) else [],
                "platform_alternatives": CrossPlatformMapper.get_5_alternatives(task_id)
            })

    return {
        "current_problem": current_problem_slug,
        "current_difficulty": curr_diff,
        "cluster_archetype": cluster_title,
        "stepping_intent": step_intent,
        "recommended_stepped_problems": recommendations
    }


@mcp.tool()
def suggest_custom_problem_concept(
    target_company: str,
    weak_topics: List[str],
    target_difficulty: str = "Medium"
) -> Dict[str, Any]:
    """
    Synthesizes historical interview patterns from the target company's question bank
    and returns a tailored problem archetype prompt for creating a custom mock question.
    """
    comp_clean = target_company.strip().lower()
    comp_df = engine.df[engine.df["companies"].apply(lambda c: comp_clean in c if isinstance(c, (list, object)) else False)]
    
    popular_tags = []
    for tags in comp_df["topic_tags"]:
        if isinstance(tags, list): popular_tags.extend(tags)
    
    top_company_tags = pd.Series(popular_tags).value_counts().head(5).index.tolist() if popular_tags else ["Array", "Dynamic Programming"]

    return {
        "target_company": target_company.upper(),
        "target_difficulty": target_difficulty,
        "weak_topics_to_target": weak_topics,
        "company_frequent_archetypes": top_company_tags,
        "synthesis_prompt": (
            f"Generate a novel interview question tailored for {target_company.title()}. "
            f"Combine the candidate's weak areas ({', '.join(weak_topics)}) with {target_company.title()}'s favorite interview patterns ({', '.join(top_company_tags)}). "
            f"Set difficulty to {target_difficulty}. Include problem description, constraints, 3 test cases, and optimal time/space complexity bounds."
        )
    }


@mcp.tool()
def push_to_web_dashboard(
    title: str,
    action_type: str,
    markdown_content: str,
    target_problem_slug: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reverse MCP Bridge: Broadcasts an action, live code review, adaptive recommendation,
    or custom interview sheet directly to the active local web host (http://localhost:8000).
    """
    payload = {
        "title": title,
        "action_type": action_type,  # 'code_review', 'adaptive_step', 'study_plan', 'alert'
        "content": markdown_content,
        "problem_slug": target_problem_slug or "",
        "timestamp": json.dumps(None)
    }

    try:
        req = urllib.request.Request(
            LOCAL_WEB_BROADCAST_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "status": "pushed_to_web",
                "message": f"Successfully broadcasted '{title}' to local Web UI at http://localhost:8000",
                "server_response": data
            }
    except Exception as e:
        return {
            "status": "broadcast_offline",
            "message": f"Web host at {LOCAL_WEB_BROADCAST_URL} is not responding (ensure web_app.py is running).",
            "error": str(e),
            "payload_saved": payload
        }


if __name__ == "__main__":
    print("Starting LeetCode DSA Intelligence MCP Server over stdio...")
    mcp.run(transport="stdio")
