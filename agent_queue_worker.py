"""
Autonomous Agent Queue Worker

Monitors 'user_queries_queue.jsonl' every 5 seconds:
1. Reads pending user queries and code submissions from the web dashboard.
2. Analyzes the problem using the LeetCode intelligence ML engine & MCP tools.
3. Generates optimal time/space complexity analysis, edge-case traps, and adaptive follow-up steps.
4. Marks the query as 'processed' in the text file.
5. Broadcasts the full solution & review back to the Web Dashboard (http://localhost:8000) in real-time!
"""

import os
import time
import json
import urllib.request
from datetime import datetime
from typing import Dict, Any, List

from ml_models import LeetCodeIntelligenceEngine
from scraper_engine import CrossPlatformMapper
import mcp_server

QUEUE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_queries_queue.jsonl")
BROADCAST_URL = "http://127.0.0.1:8000/api/agent/broadcast"

# Load intelligence engine
engine = LeetCodeIntelligenceEngine()
engine.load_models()


def read_all_queries() -> List[Dict[str, Any]]:
    """Reads all queries from the persistent JSONL queue file."""
    if not os.path.exists(QUEUE_FILE_PATH):
        return []
    
    queries = []
    with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    queries.append(json.loads(line))
                except Exception:
                    pass
    return queries


def write_all_queries(queries: List[Dict[str, Any]]) -> None:
    """Overwrites the queue file with updated query statuses."""
    with open(QUEUE_FILE_PATH, "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


def append_query(query_data: Dict[str, Any]) -> None:
    """Appends a new user query to the persistent file."""
    with open(QUEUE_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(query_data, ensure_ascii=False) + "\n")


def process_query(q: Dict[str, Any]) -> Dict[str, Any]:
    """Processes a single pending user query using ML models and MCP intelligence tools."""
    q_type = q.get("type", "general")
    slug = q.get("problem_slug", "")
    code = q.get("code", "")
    query_text = q.get("query_text", "")
    rating = q.get("rating", "moderate")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing query #{q.get('id')} ({q_type}) for '{slug or 'custom query'}'...")

    solution_output = {}

    if q_type == "code_review" or code:
        # 1. Run MCP code analysis
        analysis = mcp_server.analyze_candidate_solution(slug or "two-sum", code)
        
        # 2. Run adaptive difficulty stepper
        stepper = mcp_server.adaptive_difficulty_stepper(
            current_problem_slug=slug or "two-sum",
            performance_rating=rating,
            direction="decrease" if rating == "struggled" else ("increase" if rating == "mastered" else "similar")
        )
        
        p = engine.get_problem_by_id_or_slug(slug) or {}
        
        markdown_review = (
            f"### 📋 Autonomous AI Code Review for `{slug}`\n\n"
            f"- **Detected Patterns**: {', '.join([k.replace('uses_', '') for k, v in analysis.get('detected_patterns', {}).items() if v]) or 'Standard Iteration'}\n"
            f"- **Algorithmic Archetype**: `{analysis.get('cluster_archetype', 'General')}`\n"
            f"- **Adaptive Recommendation**: {stepper.get('stepping_intent')}\n\n"
            f"**Suggested Next Steps**:\n"
        )
        for sp in stepper.get("recommended_stepped_problems", [])[:3]:
            markdown_review += f"- **{sp['task_id']}** ({sp['difficulty']}) — [Solve Alternative]({sp['platform_alternatives'][0]['url']})\n"

        solution_output = {
            "analysis": analysis,
            "stepper": stepper,
            "markdown": markdown_review
        }

    elif q_type == "company_lookup" or "company" in q:
        comp = q.get("company", "google")
        radar = mcp_server.query_company_radar(comp, difficulty=q.get("difficulty"), topic=q.get("topic"))
        markdown_review = (
            f"### 🏢 Company Radar: `{comp.upper()}`\n\n"
            f"- **Total Directly Asked in Bank**: {radar.get('total_direct_in_dataset', 0)}\n"
            f"- **Top Novel Recommendations**: {', '.join([p['task_id'] for p in radar.get('similar_unasked_high_probability_questions', [])[:3]])}\n"
        )
        solution_output = {
            "radar": radar,
            "markdown": markdown_review
        }

    else:
        # General query or custom concept synthesis
        concept = mcp_server.suggest_custom_problem_concept("Google", ["Graph", "Sliding Window"], "Medium")
        markdown_review = (
            f"### 💡 AI Problem Synthesis\n\n"
            f"Prompt: {query_text}\n\n"
            f"**Recommended Action**: {concept.get('synthesis_prompt')}"
        )
        solution_output = {
            "concept": concept,
            "markdown": markdown_review
        }

    # Broadcast solution live to Web Dashboard
    try:
        payload = {
            "title": f"AI Solution: {slug or 'User Query'}",
            "action_type": "code_review" if code else "study_plan",
            "content": solution_output.get("markdown", "Query processed successfully."),
            "problem_slug": slug or ""
        }
        req = urllib.request.Request(
            BROADCAST_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Broadcasted solution to Web Dashboard!")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Web broadcast skipped (dashboard offline): {e}")

    return solution_output


def run_worker_loop(poll_seconds: int = 5, max_iterations: int = None):
    """Continuously polls user_queries_queue.jsonl every 5 seconds."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting 5-Second Agent Queue Worker...")
    print(f"Monitoring: {QUEUE_FILE_PATH}")
    
    iterations = 0
    while True:
        try:
            queries = read_all_queries()
            updated = False
            
            for q in queries:
                if q.get("status") == "pending":
                    solution = process_query(q)
                    q["status"] = "processed"
                    q["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    q["solution"] = solution
                    updated = True

            if updated:
                write_all_queries(queries)

        except Exception as e:
            print(f"Error in worker loop: {e}")

        iterations += 1
        if max_iterations and iterations >= max_iterations:
            break

        time.sleep(poll_seconds)


if __name__ == "__main__":
    run_worker_loop(poll_seconds=5)
