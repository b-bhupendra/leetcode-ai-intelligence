"""
Test Suite for Persistent Query Queue and 5-Second Agent Worker
"""

import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from web_app import app
import agent_queue_worker

def test_queue_and_worker():
    print("=== Testing Persistent User Query Queue & 5-Second Agent Worker ===")
    client = TestClient(app)

    # 1. Submit a user query to queue
    print("\n--- Test 1: Submit Query via API ---")
    r_sub = client.post("/api/agent/submit-query", json={
        "query_type": "code_review",
        "problem_slug": "two-sum",
        "code": "def twoSum(nums, target):\n    d = {}\n    for i, n in enumerate(nums):\n        if target-n in d: return [d[target-n], i]\n        d[n] = i",
        "rating": "mastered"
    })
    assert r_sub.status_code == 200
    entry = r_sub.json()["entry"]
    assert entry["status"] == "pending"
    print(f" [PASS] Submitted query #{entry['id']} to {agent_queue_worker.QUEUE_FILE_PATH}")

    # 2. Check that file contains the query
    queries = agent_queue_worker.read_all_queries()
    assert len(queries) > 0
    assert any(q["id"] == entry["id"] for q in queries)
    print(f" [PASS] Persistent file verified ({len(queries)} total queries in log).")

    # 3. Process the query with the agent worker
    print("\n--- Test 2: Process Query via Agent Worker ---")
    agent_queue_worker.run_worker_loop(poll_seconds=1, max_iterations=1)

    # Verify query status is updated to 'processed'
    updated_queries = agent_queue_worker.read_all_queries()
    processed_entry = [q for q in updated_queries if q["id"] == entry["id"]][0]
    assert processed_entry["status"] == "processed"
    assert "solution" in processed_entry
    assert "markdown" in processed_entry["solution"]
    print(f" [PASS] Query #{entry['id']} successfully solved, marked 'processed', and broadcasted!")

    # 4. Check that Web Dashboard Queue API returns processed status
    r_q = client.get("/api/agent/queue")
    assert r_q.status_code == 200
    q_list = r_q.json()["queries"]
    assert any(q["id"] == entry["id"] and q["status"] == "processed" for q in q_list)
    print(f" [PASS] GET /api/agent/queue returned updated records.")

    print("\n ALL USER QUERY QUEUE & 5-SECOND AGENT WORKER TESTS PASSED!")

if __name__ == "__main__":
    test_queue_and_worker()
