# LeetCode AI Intelligence Platform

An end-to-end Machine Learning, Clustering, Classification, and Recommendation system built on top of:
1. **Hugging Face `newfacade/LeetCodeDataset`** (2,869 rich Python LeetCode problems).
2. **GitHub `krishnadey30/LeetCode-Questions-CompanyWise`** (Company interview frequency data across 200 companies).

---

## 🌟 Key Capabilities

### 1. 🧠 Multi-Label Company Classifier
Predicts which tech companies (e.g. Google, Amazon, Meta, Microsoft, Uber, Roblox, etc.) are most likely to ask a coding problem based on its description, algorithmic tags, difficulty, and code signature.
- Provides calibrated match scores (0–100%).
- Automatically assigns the problem to one of 30 algorithmic archetypes.
- Explains the rationale behind the prediction.

### 2. 🔍 Smart Filter & "Similar Unasked Problem" Discovery
Filters problems by Company, Difficulty, and Topic, and delivers two complementary views:
- **🎯 Directly Asked Questions**: Real recorded interview questions asked by that company.
- **💡 Similar High-Probability Questions (Novel / Unasked)**: Discovers questions that have *never* been explicitly recorded for that company in the dataset, but share highest structural, algorithmic, and semantic similarity with the company's interview style ("they ask that kind of question").

### 3. 🌐 30 Algorithmic Archetype Clusters
All 2,869 LeetCode problems grouped into thematic interview clusters (e.g. *Graph & DFS*, *Sliding Window & Two Pointers*, *Dynamic Programming on Subsequences*, *Interval Scheduling*).

---

## 📁 Repository Structure

```
leetcode_dataset_merger/
├── models/                                      # Serialized ML Models
│   ├── feature_extractor.joblib                 # Multi-modal TF-IDF + Tag + Diff vectorizer
│   ├── company_classifier.joblib                # Multi-label supervised + centroid classifier
│   ├── cluster_engine.joblib                    # 30-cluster KMeans & NearestNeighbors index
│   └── X_features.joblib                        # Normalized feature embeddings matrix
├── output/                                      # Merged Datasets
│   ├── leetcode_with_companies_full.parquet     # Full dataset with code/tests
│   ├── leetcode_with_companies_summary.csv      # Lightweight metadata CSV
│   ├── company_problem_matrix.parquet / .csv    # Relational company-problem table (20,453 rows)
│   ├── company_statistics_summary.csv           # 200 companies interview frequency summary
│   ├── leetcode_with_companies_report.xlsx      # Multi-sheet Excel workbook
│   └── leetcode_with_companies_full.jsonl       # Full JSONL format
├── templates/
│   └── index.html                               # Modern Dark-Mode SPA Web Dashboard
├── ml_models.py                                 # Core ML Pipeline & Intelligence Engine
├── web_app.py                                   # FastAPI Web Application Backend
├── load_data.py                                 # Pandas data loader utilities
├── merge_datasets.py                            # ETL data merge script
├── test_ml_pipeline.py                          # Automated ML test suite
├── test_web_api.py                              # Automated API test suite
├── test_merged_data.py                          # Dataset integrity test suite
└── requirements.txt                             # Python dependencies
```

---

## 🚀 How to Run the Web Dashboard

To launch the interactive web dashboard on `http://localhost:8000`:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run FastAPI web app
python web_app.py
```
Open **`http://localhost:8000`** in your browser to interact with:
1. **Company Predictor**: Paste any problem text to get instant company probability rankings.
2. **Smart Filter & Discovery**: Filter by company/topic/difficulty and explore direct matches alongside similar novel problems.
3. **Archetype Clusters**: Explore all 30 algorithmic problem archetypes.

---

## 🐍 Python API Usage

### 1. Predict Companies for a New Problem
```python
from ml_models import LeetCodeIntelligenceEngine

engine = LeetCodeIntelligenceEngine()
engine.load_models()

desc = """
There are n cities. Given roads array with travel times, find the minimum
time to travel from city 0 to city n-1 with at most k stops.
"""

result = engine.predict_problem_companies(
    problem_description=desc,
    title="minimum-cost-route-with-stops",
    difficulty="Medium",
    topic_tags=["Graph", "Shortest Path", "Heap (Priority Queue)"],
    top_k=5
)

print(f"Assigned Cluster: {result['assigned_cluster']['cluster_title']}")
for pred in result["predicted_companies"]:
    print(f"- {pred['company']}: {pred['confidence_score']}% match ({pred['rationale']})")
```

### 2. Filter by Company & Discover Similar Unasked Problems
```python
# Find Google Medium Graph questions + similar novel questions
res = engine.filter_and_recommend(
    company="google",
    difficulty="Medium",
    topic="Graph",
    max_direct=10,
    max_similar=5
)

print(f"Direct Google Questions: {res['direct_count']}")
for p in res["direct_problems"]:
    print(f"  [Direct] {p['task_id']} (Freq: {p['frequency']})")

print(f"\nSimilar High-Probability Questions (NOT asked at Google in dataset):")
for p in res["similar_unasked_problems"]:
    print(f"  [Similar] {p['task_id']} (Similarity: {p['similarity_score']}%)")
```

---

## 🧪 Verification & Automated Tests

To run all automated verification suites:
```bash
# Test dataset integrity (Parquet, CSV, Excel, JSONL)
python test_merged_data.py

# Test ML pipeline (Classification, Clustering, Recommendations)
python test_ml_pipeline.py

# Test FastAPI web endpoints
python test_web_api.py
```
*(All tests passing 100%)*
