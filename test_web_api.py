"""
Comprehensive Verification of Updated FastAPI Web Endpoints & Cross-Platform Engine
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from web_app import app

def test_web_api():
    client = TestClient(app)
    print("=== Testing FastAPI REST Endpoints & Cross-Platform Engine ===")

    # 1. Metadata Endpoint
    r_meta = client.get("/api/metadata")
    assert r_meta.status_code == 200
    meta = r_meta.json()
    print(f" [PASS] /api/metadata: {len(meta['companies'])} companies, {meta['total_problems']} problems, {meta['clusters_count']} clusters.")

    # 2. Predict Endpoint with 5 Platforms & Similar Counterparts
    r_pred = client.post("/api/predict", json={
        "title": "cheapest-flights-within-k-stops",
        "description": "There are n cities connected by some number of flights. You are given an array flights where flights[i] = [from, to, price] represents that there is a flight from city from to city to with cost price. Find the cheapest price from src to dst with at most k stops.",
        "difficulty": "Medium",
        "topic_tags": ["Dynamic Programming", "Depth-First Search", "Breadth-First Search", "Graph", "Heap (Priority Queue)", "Shortest Path"]
    })
    assert r_pred.status_code == 200
    pred = r_pred.json()["data"]
    assert len(pred["predicted_companies"]) > 0
    assert len(pred["platform_alternatives"]) == 5, f"Expected 5 platform alternatives, got {len(pred['platform_alternatives'])}"
    print(f" [PASS] /api/predict: Cluster '{pred['assigned_cluster']['cluster_title']}', 5 Platform Alternatives, {len(pred['similar_existing_problems'])} similar counterparts.")

    # 3. Filter & Recommend Endpoint
    r_filt = client.post("/api/filter-recommend", json={
        "company": "google",
        "difficulty": "Medium",
        "topic": "Graph"
    })
    assert r_filt.status_code == 200
    filt = r_filt.json()["data"]
    assert filt["direct_count"] > 0
    assert filt["similar_unasked_count"] > 0
    first_direct = filt["direct_problems"][0]
    assert len(first_direct["platform_alternatives"]) == 5
    print(f" [PASS] /api/filter-recommend: {filt['direct_count']} direct Google problems, {filt['similar_unasked_count']} similar unasked problems.")

    # 4. Detailed Problem Lookup Endpoint (/api/problem/{id})
    r_prob = client.get("/api/problem/two-sum")
    assert r_prob.status_code == 200
    prob_data = r_prob.json()["data"]
    assert prob_data["task_id"] == "two-sum"
    assert len(prob_data["platform_alternatives"]) == 5
    assert len(prob_data["similar_counterparts"]) == 5
    print(f" [PASS] /api/problem/two-sum: Loaded problem specifications, 5 platforms, and 5 similar counterparts.")

    # 5. Single Scrape & Ingest Endpoint
    r_scrape = client.post("/api/scrape-and-ingest", json={"slug_or_url": "longest-common-subsequence"})
    assert r_scrape.status_code == 200
    scrape_res = r_scrape.json()
    print(f" [PASS] /api/scrape-and-ingest: {scrape_res.get('message', 'Ingest OK')}")

    # 6. Background Crawler Controller Endpoints
    r_toggle = client.post("/api/crawler/toggle", json={"enable": True})
    assert r_toggle.status_code == 200
    assert r_toggle.json()["crawler_running"] == True

    r_status = client.get("/api/crawler/status")
    assert r_status.status_code == 200
    status_data = r_status.json()["data"]
    assert status_data["is_running"] == True

    # Stop crawler
    client.post("/api/crawler/toggle", json={"enable": False})
    print(f" [PASS] /api/crawler: Started, queried status ({status_data['total_problems_in_db']} problems in DB), and stopped cleanly.")

    # 7. Index HTML Page
    r_idx = client.get("/")
    assert r_idx.status_code == 200
    assert "LeetCode AI Intelligence" in r_idx.text
    print(" [PASS] Root UI template served cleanly.")

    print("\n ALL WEB API AND SCRAPER ENDPOINTS VERIFIED AND PASSING!")

if __name__ == "__main__":
    test_web_api()
