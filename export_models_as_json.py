"""
Export Machine Learning Models as Pure Plain-Text JSON (Zero Binaries)

Converts all ML classifiers, cluster archetypes, company centroids,
and tag vocabularies into human and LLM-readable JSON files:
1. models/archetype_clusters.json
2. models/company_profiles.json
3. models/topic_vocabulary.json
4. models/difficulty_rules.json
"""

import os
import json
import pandas as pd
from ml_models import LeetCodeIntelligenceEngine

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def export_plain_text_models():
    print("=== Exporting ML Models to Pure Plain-Text JSON ===")
    engine = LeetCodeIntelligenceEngine()
    engine.load_models()

    # 1. Export 15 Unified Algorithmic Archetype Clusters with 5 Difficulty Tiers & GFG Roadmap
    clusters_json_path = os.path.join(MODELS_DIR, "archetype_clusters.json")
    with open(clusters_json_path, "w", encoding="utf-8") as f:
        json.dump(engine.cluster_engine.cluster_summaries, f, indent=2, ensure_ascii=False)
    print(f" [OK] Exported 15 Archetypes -> {clusters_json_path} ({os.path.getsize(clusters_json_path):,} bytes)")

    # 2. Export Company Interview Profiles & Centroids
    company_profiles = {}
    for comp in sorted(list(engine.company_classifier.target_companies)):
        comp_df = engine.df[engine.df["companies"].apply(lambda c: comp in c if isinstance(c, (list, object)) else False)]
        
        # Calculate topic frequencies for company
        all_tags = []
        for tags in comp_df["topic_tags"]:
            if isinstance(tags, list): all_tags.extend(tags)
        
        top_tags = pd.Series(all_tags).value_counts().head(8).to_dict() if all_tags else {}
        top_probs = comp_df.sort_values(by="companies_count", ascending=False)["task_id"].head(5).tolist()

        company_profiles[comp] = {
            "company_name": comp.upper(),
            "total_questions_in_bank": len(comp_df),
            "primary_topics": top_tags,
            "signature_problems": top_probs,
            "interview_focus": f"High frequency on {', '.join(list(top_tags.keys())[:3]) or 'General Algorithms'}"
        }

    company_json_path = os.path.join(MODELS_DIR, "company_profiles.json")
    with open(company_json_path, "w", encoding="utf-8") as f:
        json.dump(company_profiles, f, indent=2, ensure_ascii=False)
    print(f" [OK] Exported {len(company_profiles)} Company Profiles -> {company_json_path} ({os.path.getsize(company_json_path):,} bytes)")

    # 3. Export Topic Vocabulary & Rules
    all_known_topics = sorted(list(set(engine.topic_classifier.mlb.classes_))) if hasattr(engine.topic_classifier, 'mlb') else []
    topic_rules = {
        "total_supported_topics": len(all_known_topics),
        "topics": all_known_topics,
        "classification_strategy": "TF-IDF N-Gram Pattern Matching & Logistic Multi-Label Thresholding"
    }
    topic_json_path = os.path.join(MODELS_DIR, "topic_vocabulary.json")
    with open(topic_json_path, "w", encoding="utf-8") as f:
        json.dump(topic_rules, f, indent=2, ensure_ascii=False)
    print(f" [OK] Exported Topic Vocabulary -> {topic_json_path}")

    # 4. Export 5-Tier Difficulty Heuristics & Rules
    diff_rules = {
        "classes": ["Easy", "Easy-Medium", "Medium", "Medium-Hard", "Hard"],
        "heuristics": {
            "Easy": "Tier 1: Direct single-pass arrays, basic hash table lookups, elementary math / string formatting",
            "Easy-Medium": "Tier 2: Easy with algorithmic twists (two pointers / basic DP) or short standard Mediums",
            "Medium": "Tier 3: Core Medium questions (Tree/Graph BFS/DFS, Binary Search, Sliding Window, Greedy)",
            "Medium-Hard": "Tier 4: Advanced Mediums (1D DP, Segment Trees, Bitmasks) or approachable Hard questions",
            "Hard": "Tier 5: Deep multi-dimensional DP, Complex Segment Trees, Network Flows, Game Theory"
        }
    }
    diff_json_path = os.path.join(MODELS_DIR, "difficulty_rules.json")
    with open(diff_json_path, "w", encoding="utf-8") as f:
        json.dump(diff_rules, f, indent=2, ensure_ascii=False)
    print(f" [OK] Exported 5-Tier Difficulty Rules -> {diff_json_path}")

    print("\n ALL ML MODELS SUCCESSFULLY CONVERTED TO PLAIN-TEXT JSON!")


if __name__ == "__main__":
    export_plain_text_models()
