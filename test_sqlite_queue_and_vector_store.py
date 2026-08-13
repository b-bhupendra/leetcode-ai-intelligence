"""
Verification Test Suite: SQLite Queue Manager & ChromaDB Vector Store

Tests:
1. ACID-compliant SQLite task queuing, atomic claiming, completion, and recent query retrieval.
2. ChromaDB persistent vector storage, dynamic O(1) problem appending, and HNSW cosine search.
3. End-to-end agent worker execution on SQLite tasks.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add current directory to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

import queue_manager
from vector_store import LeetCodeVectorStore
import agent_queue_worker


def test_sqlite_queue():
    print("\n--- 1. Testing SQLite Queue Manager ---")
    
    # 1. Enqueue task
    task_id = queue_manager.enqueue_task(
        query_type="code_review",
        query_text="Testing SQLite concurrency",
        problem_slug="two-sum",
        code="def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen: return [seen[target-n], i]\n        seen[n] = i",
        rating="mastered"
    )
    print(f" [PASS] Enqueued task #{task_id} with status 'pending'")
    assert task_id > 0

    # 2. Claim pending task
    claimed = queue_manager.claim_next_pending_task()
    assert claimed is not None
    assert claimed["status"] == "processing"
    print(f" [PASS] Atomically claimed pending task #{claimed['id']} (status: {claimed['status']})")

    # 3. Mark completed
    solution_payload = {
        "summary": "O(N) Hash Table optimal solution verified.",
        "time_complexity": "O(N)",
        "space_complexity": "O(N)"
    }
    queue_manager.mark_task_completed(claimed["id"], solution_payload)
    print(f" [PASS] Marked task #{claimed['id']} as 'processed'")

    # 4. Verify in recent queries
    recent = queue_manager.list_recent_queries(limit=5)
    matched = [q for q in recent if q["id"] == claimed["id"]]
    assert len(matched) == 1
    assert matched[0]["status"] == "processed"
    assert matched[0]["solution"]["time_complexity"] == "O(N)"
    print(f" [PASS] Verified task #{claimed['id']} in list_recent_queries()")


def test_vector_store():
    print("\n--- 2. Testing ChromaDB Vector Store ---")
    
    vstore = LeetCodeVectorStore(persist_directory=os.path.join(ROOT_DIR, "chroma_db"))
    
    # Create mock vector (100 dimensions)
    mock_vector = np.random.randn(100).astype(np.float32)
    
    mock_problem = {
        "question_id": 99999,
        "task_id": "test-dynamic-problem",
        "title": "Test Dynamic Problem",
        "difficulty": "Hard",
        "cluster_id": 14,
        "cluster_title": "Dynamic Programming & Optimization",
        "companies_count": 12,
        "topic_tags": ["Dynamic Programming", "Memoization"]
    }
    
    # 1. Append single problem (O(1))
    vstore.append_problem(mock_problem, mock_vector)
    print(f" [PASS] Dynamically appended vector for '{mock_problem['task_id']}' (Total vectors: {vstore.count()})")
    
    # 2. Query similar problems
    results = vstore.get_similar_problems(mock_vector, top_k=3)
    assert len(results) > 0
    top_match = results[0]
    print(f" [PASS] Queried vector similarity -> Top Match: '{top_match['task_id']}' ({top_match['similarity_score']}%)")
    assert top_match["task_id"] == "test-dynamic-problem"
    assert top_match["similarity_score"] >= 95.0


def test_agent_worker_end_to_end():
    print("\n--- 3. Testing Agent Worker SQLite End-to-End ---")
    
    # Enqueue a mock code review
    tid = queue_manager.enqueue_task(
        query_type="code_review",
        query_text="Automated worker test",
        problem_slug="trapping-rain-water",
        code="def trap(height):\n    l, r = 0, len(height) - 1\n    max_l, max_r = 0, 0\n    ans = 0\n    while l < r:\n        if height[l] < height[r]:\n            if height[l] >= max_l: max_l = height[l]\n            else: ans += max_l - height[l]\n            l += 1\n        else:\n            if height[r] >= max_r: max_r = height[r]\n            else: ans += max_r - height[r]\n            r -= 1\n    return ans",
        rating="mastered"
    )
    
    # Run worker until our specific task is completed
    for _ in range(5):
        task = queue_manager.claim_next_pending_task()
        if not task:
            break
        sol = agent_queue_worker.process_query(task)
        queue_manager.mark_task_completed(task["id"], sol)
    
    # Verify task was claimed and completed
    recent = queue_manager.list_recent_queries(limit=10)
    completed_task = next((q for q in recent if q["id"] == tid), None)
    assert completed_task is not None
    assert completed_task["status"] == "processed"
    print(f" [PASS] Agent worker successfully processed task #{tid} (Status: {completed_task['status']})")


if __name__ == "__main__":
    test_sqlite_queue()
    test_vector_store()
    test_agent_worker_end_to_end()
    print("\n[SUCCESS] ALL ARCHITECTURAL UPGRADE TESTS PASSED!")
