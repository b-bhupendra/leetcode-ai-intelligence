"""
Autonomous Agent Queue Worker (Hardened SQLite Edition)

Monitors the transactional SQLite queue every 5 seconds:
1. Atomically claims pending user queries and code submissions from the web dashboard.
2. Analyzes the problem using the LeetCode intelligence ML engine & FastMCP tools.
3. Generates optimal time/space complexity analysis, edge-case traps, and adaptive follow-up steps.
4. Marks the query as 'processed' in the SQLite database with full ACID compliance.
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
import queue_manager

BROADCAST_URL = "http://127.0.0.1:8000/api/agent/broadcast"

# Load intelligence engine
engine = LeetCodeIntelligenceEngine()
engine.load_models()


def process_query(q: Dict[str, Any]) -> Dict[str, Any]:
    """Processes a single claimed user query using ML models and MCP intelligence tools."""
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

    elif q_type == "custom_mock_problem":
        # Run custom concept synthesis tool
        concept = mcp_server.suggest_custom_problem_concept(
            target_company=query_text or "google",
            weak_topics=["Dynamic Programming", "Graph"],
            target_difficulty=rating.capitalize() if rating in ["easy", "medium", "hard"] else "Medium"
        )
        solution_output = {
            "concept": concept,
            "markdown": f"### 🎯 Custom Interview Mock: {concept.get('generated_concept', {}).get('title')}\n\n{concept.get('generated_concept', {}).get('problem_premise')}"
        }

    else:
        # General query / similarity radar
        specs = mcp_server.get_problem_full_specs(slug or "two-sum") if slug else {}
        radar = mcp_server.query_company_radar(company=query_text or "google", limit=3)
        solution_output = {
            "specs": specs,
            "radar": radar,
            "markdown": f"### 📊 Intelligence Radar Report for '{query_text or slug}'\n\nRetrieved specs & interview radar metrics successfully."
        }

    return solution_output


def broadcast_to_web_dashboard(title: str, action_type: str, markdown: str, target_slug: str = ""):
    """Broadcasts the solved result to the web dashboard via FastAPI SSE bridge."""
    try:
        payload = json.dumps({
            "title": title,
            "action_type": action_type,
            "markdown": markdown,
            "target_problem_slug": target_slug
        }).encode("utf-8")

        req = urllib.request.Request(
            BROADCAST_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Worker] Web broadcast notice: Dashboard offline or not listening yet ({e})")
        return False


def run_agent_loop(interval_seconds: float = 5.0, max_iterations: int = None):
    """Continuous agent loop polling the transactional SQLite queue."""
    print(f"[START] Autonomous SQLite Worker started. Polling every {interval_seconds}s...")
    iterations = 0

    while True:
        try:
            # Atomically claim the oldest pending task
            task = queue_manager.claim_next_pending_task()
            
            if task:
                task_id = task["id"]
                try:
                    # Process task
                    solution = process_query(task)
                    
                    # Mark complete in SQLite
                    queue_manager.mark_task_completed(task_id, solution)
                    
                    # Broadcast live to Web Dashboard
                    broadcast_to_web_dashboard(
                        title=f"Autonomous AI Solution for #{task_id} ({task.get('problem_slug') or 'Custom Query'})",
                        action_type="agent_solution_push",
                        markdown=solution.get("markdown", "Solution processed successfully."),
                        target_slug=task.get("problem_slug", "")
                    )
                    print(f" [OK] Query #{task_id} completed and broadcasted.")
                except Exception as ex:
                    print(f" [ERROR] Error processing query #{task_id}: {ex}")
                    queue_manager.mark_task_failed(task_id, str(ex))
            else:
                # No pending tasks, wait for next tick
                time.sleep(interval_seconds)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break

        except KeyboardInterrupt:
            print("[AgentWorker] Stopping worker gracefully...")
            break
        except Exception as e:
            print(f"[AgentWorker] Queue loop error: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    run_agent_loop(interval_seconds=5.0)
