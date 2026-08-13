"""
Test Suite for Scraper, Cross-Platform Alternatives, and Auto-Classification Engine
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from scraper_engine import CrossPlatformMapper, LeetCodeScraper, ContinuousIngestionWorker
from ml_models import LeetCodeIntelligenceEngine

def test_pipeline():
    print("=== Testing Scraper, Cross-Platform Alternatives & Auto-Classifier ===")

    # 1. Test Cross-Platform Alternatives
    print("\n--- Test 1: Cross-Platform Alternatives Generation ---")
    alts = CrossPlatformMapper.get_5_alternatives("trapping-rain-water", "Trapping Rain Water", "Two Pointers")
    assert len(alts) == 5, f"Expected 5 alternatives, got {len(alts)}"
    platforms = [a["platform"] for a in alts]
    print(f"Generated 5 alternatives across: {platforms}")
    for a in alts:
        print(f"  - [{a['platform']}]: {a['url']}")
    assert "LeetCode" in platforms and "GeeksforGeeks" in platforms and "LintCode" in platforms and "HackerRank" in platforms and "CodeStudio (Naukri 360)" in platforms
    print(" [PASS] 5 Cross-Platform Alternatives verified.")

    # 2. Test Auto-Classification of Raw Unannotated Problem
    print("\n--- Test 2: Auto-Classification of Raw Unannotated Problem ---")
    engine = LeetCodeIntelligenceEngine()
    engine.load_models()

    raw_problem = {
        "task_id": "network-connected-components-count",
        "title": "Network Connected Components Count",
        "difficulty": None,  # Model will predict Difficulty!
        "topic_tags": [],    # Model will predict Topics!
        "problem_description": "There are n computers numbered from 0 to n-1 and an array of connections where connections[i] = [a, b]. Return the total number of connected network components using Union Find or Depth First Search."
    }

    enriched = engine.autoclassify_and_enrich(raw_problem)
    print(f"Auto-Predicted Difficulty: {enriched['difficulty']}")
    print(f"Auto-Predicted Topic Tags: {enriched['topic_tags']}")
    print(f"Auto-Assigned Cluster:     {enriched['cluster_title']}")
    print(f"Top Predicted Companies:   {enriched['top_companies'][:4]}")
    print(f"Cross-Platform Links:      {len(enriched['platform_alternatives'])} platforms")
    print(f"Similar Counterparts:      {len(enriched['similar_counterparts'])} problems")

    assert enriched["difficulty"] in ["Easy", "Medium", "Hard"], "Difficulty was not predicted!"
    assert len(enriched["topic_tags"]) > 0, "Topics were not predicted!"
    assert len(enriched["platform_alternatives"]) == 5, "5 alternatives missing!"
    assert len(enriched["similar_counterparts"]) == 5, "5 similar counterparts missing!"
    print(" [PASS] Autonomous Problem Classification & Enrichment verified.")

    # 3. Test Dynamic Append and Search Re-indexing
    print("\n--- Test 3: Dynamic Database Ingestion & Re-indexing ---")
    initial_db_size = len(engine.df)
    engine.append_and_reindex(enriched)
    new_db_size = len(engine.df)
    assert new_db_size == initial_db_size + 1, f"Expected DB size {initial_db_size+1}, got {new_db_size}"
    
    # Test searching for the newly appended problem
    found = engine.get_problem_by_id_or_slug("network-connected-components-count")
    assert found is not None, "Newly ingested problem could not be retrieved!"
    print(f" [PASS] Database expanded from {initial_db_size} to {new_db_size} problems and verified.")

    # 4. Test Background Ingestion Worker Status
    print("\n--- Test 4: Background Ingestion Worker ---")
    worker = ContinuousIngestionWorker(engine, poll_interval_seconds=10)
    status = worker.get_status()
    print(f"Worker status: Running={status['is_running']}, ProblemsInDB={status['total_problems_in_db']}, RemainingInPool={status['pool_remaining']}")
    assert status["total_problems_in_db"] == new_db_size
    print(" [PASS] Worker Status verified.")

    print("\n ALL SCRAPER & AUTO-CLASSIFIER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline()
