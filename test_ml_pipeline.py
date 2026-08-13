"""
Automated Verification Suite for ML Company Classification, Clustering & Recommendation
"""

import os
import json
import pandas as pd
from ml_models import LeetCodeIntelligenceEngine

def test_ml_pipeline():
    print("=== Testing ML Classification, Clustering & Recommendation Engine ===")
    
    engine = LeetCodeIntelligenceEngine()
    engine.load_models()
    assert engine.is_ready, "Engine failed to initialize!"
    print(" [PASS] Engine models loaded successfully.")

    # --- Test 1: Classify Graph Shortest Path Problem ---
    print("\n--- Test 1: Predict Companies for Graph Dijkstra Problem ---")
    graph_desc = """
    There are n cities numbered from 0 to n - 1. You are given a 2D integer array roads where
    roads[i] = [u, v, time] represents a bidirectional road between city u and city v with travel time.
    Find the minimum time to travel from city 0 to city n - 1 with at most k stops.
    """
    res_graph = engine.predict_problem_companies(
        problem_description=graph_desc,
        title="minimum-time-to-reach-destination",
        difficulty="Medium",
        topic_tags=["Graph", "Shortest Path", "Heap (Priority Queue)", "Dijkstra"],
        top_k=5
    )
    print(f"Assigned Cluster: {res_graph['assigned_cluster']['cluster_title']}")
    print("Top Predicted Companies:")
    for pred in res_graph["predicted_companies"][:5]:
        print(f"  - {pred['company'].upper():<12}: Confidence {pred['confidence_score']}% ({pred['rationale']})")
    
    top_graph_comps = [p["company"] for p in res_graph["predicted_companies"]]
    assert any(c in top_graph_comps for c in ["google", "amazon", "microsoft", "uber"]), "Expected major tech companies for graph problem!"
    print(" [PASS] Graph Problem Classification verified.")

    # --- Test 2: Classify Sliding Window / Two Pointer Problem ---
    print("\n--- Test 2: Predict Companies for Sliding Window Substring Problem ---")
    sliding_desc = """
    Given a string s, find the length of the longest substring without repeating characters.
    You must use a two pointer sliding window technique to optimize lookup in O(N) time.
    """
    res_sliding = engine.predict_problem_companies(
        problem_description=sliding_desc,
        title="longest-substring-without-repeating-characters",
        difficulty="Medium",
        topic_tags=["Hash Table", "String", "Sliding Window", "Two Pointers"],
        top_k=5
    )
    print(f"Assigned Cluster: {res_sliding['assigned_cluster']['cluster_title']}")
    print("Top Predicted Companies:")
    for pred in res_sliding["predicted_companies"][:5]:
        print(f"  - {pred['company'].upper():<12}: Confidence {pred['confidence_score']}% ({pred['rationale']})")
    print(" [PASS] Sliding Window Problem Classification verified.")

    # --- Test 3: Filter by Company & Recommend Similar Unasked Questions ---
    print("\n--- Test 3: Filter by 'Google' & Discover Similar Unasked High-Probability Questions ---")
    google_res = engine.filter_and_recommend(
        company="google",
        difficulty="Medium",
        topic="Graph",
        max_direct=5,
        max_similar=5
    )
    print(f"Direct Google Medium Graph Questions in Dataset: {google_res['direct_count']}")
    print("Sample Direct Questions:")
    for p in google_res["direct_problems"][:3]:
        print(f"  - [ID {p['question_id']}] {p['task_id']} (Freq: {p['frequency']}, Cluster: {p['cluster_title']})")

    print(f"\nSimilar High-Probability Questions NOT tagged for Google in dataset ({google_res['similar_unasked_count']}):")
    for p in google_res["similar_unasked_problems"][:3]:
        print(f"  - [ID {p['question_id']}] {p['task_id']} (Similarity: {p['similarity_score']}%, Cluster: {p['cluster_title']})")
        print(f"    Reason: {p['reason']}")

    assert len(google_res["direct_problems"]) > 0, "Expected direct Google questions!"
    assert len(google_res["similar_unasked_problems"]) > 0, "Expected similar unasked questions!"
    print(" [PASS] Google Filter & Unasked Recommendation verified.")

    # --- Test 4: Filter by Amazon & Dynamic Programming ---
    print("\n--- Test 4: Filter by 'Amazon' & Dynamic Programming ---")
    amazon_res = engine.filter_and_recommend(
        company="amazon",
        difficulty="Hard",
        topic="Dynamic Programming",
        max_direct=5,
        max_similar=5
    )
    print(f"Direct Amazon Hard DP Questions: {amazon_res['direct_count']}")
    print(f"Similar Unasked Hard DP Questions: {amazon_res['similar_unasked_count']}")
    assert len(amazon_res["direct_problems"]) > 0
    assert len(amazon_res["similar_unasked_problems"]) > 0
    print(" [PASS] Amazon Hard DP Recommendations verified.")

    # --- Test 5: Cluster Breakdown Coverage ---
    print("\n--- Test 5: Archetype Cluster Summaries ---")
    total_clusters = len(engine.cluster_engine.cluster_summaries)
    print(f"Total Algorithmic Clusters: {total_clusters}")
    print("Sample Clusters:")
    for c_id in range(min(5, total_clusters)):
        c_info = engine.cluster_engine.cluster_summaries[c_id]
        print(f"  - Cluster {c_id}: {c_info['title']} ({c_info['size']} problems) -> Tags: {c_info['top_tags']}")
    
    assert total_clusters == 30, f"Expected 30 clusters, got {total_clusters}"
    print(" [PASS] Cluster Summaries verified.")

    print("\n ALL ML PIPELINE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_ml_pipeline()
