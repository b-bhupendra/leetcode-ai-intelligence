"""
Machine Learning Pipeline for LeetCode Problem Classification, Clustering,
Cross-Platform Alternatives, and Company-Aware Similar Problem Recommendation Engine.
"""

import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, normalize
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack, csr_matrix, vstack

from scraper_engine import CrossPlatformMapper

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def clean_text(text: str) -> str:
    """Cleans HTML tags, Markdown symbols, and normalizes whitespace."""
    if not text or pd.isna(text):
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"[^\w\s\-\+\*\/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


class LeetCodeFeatureExtractor:
    """
    Extracts multi-modal features combining problem descriptions, topic tags,
    and difficulty into normalized feature vectors.
    """
    def __init__(self, max_text_features: int = 8000):
        self.max_text_features = max_text_features
        self.text_vectorizer = TfidfVectorizer(
            max_features=max_text_features,
            sublinear_tf=True,
            ngram_range=(1, 2),
            stop_words="english",
            min_df=2,
            max_df=0.95
        )
        self.tag_binarizer = MultiLabelBinarizer()
        self.diff_encoder = OneHotEncoder(sparse_output=True, handle_unknown="ignore")
        self.is_fitted = False

    def _prepare_text_corpus(self, df: pd.DataFrame) -> List[str]:
        corpus = []
        for _, row in df.iterrows():
            title = str(row.get("task_id", "")).replace("-", " ")
            desc = clean_text(row.get("problem_description", ""))
            
            # Extract starter code signature
            starter = str(row.get("starter_code", ""))
            func_sigs = " ".join(re.findall(r"def\s+([a-zA-Z0-9_]+)", starter))
            
            # Algorithmic topic tags
            tags = row.get("topic_tags", [])
            if isinstance(tags, (list, np.ndarray)):
                tags_str = " ".join([str(t).lower() for t in tags])
            else:
                tags_str = str(tags).replace(";", " ")
                
            combined = f"{title} {title} {tags_str} {tags_str} {func_sigs} {desc}"
            corpus.append(combined)
        return corpus

    def _prepare_tags(self, df: pd.DataFrame) -> List[List[str]]:
        tag_lists = []
        for _, row in df.iterrows():
            tags = row.get("topic_tags", [])
            if isinstance(tags, (list, np.ndarray)):
                clean_tags = [str(t).strip() for t in tags if str(t).strip()]
            elif isinstance(tags, str) and tags.strip():
                clean_tags = [t.strip() for t in tags.split(";") if t.strip()]
            else:
                clean_tags = []
            tag_lists.append(clean_tags)
        return tag_lists

    def _prepare_diff(self, df: pd.DataFrame) -> np.ndarray:
        diffs = df[["difficulty"]].fillna("Medium").to_numpy()
        return diffs

    def fit(self, df: pd.DataFrame):
        corpus = self._prepare_text_corpus(df)
        self.text_vectorizer.fit(corpus)

        tags = self._prepare_tags(df)
        self.tag_binarizer.fit(tags)

        diffs = self._prepare_diff(df)
        self.diff_encoder.fit(diffs)

        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> csr_matrix:
        if not self.is_fitted:
            raise ValueError("Feature extractor is not fitted yet.")

        corpus = self._prepare_text_corpus(df)
        text_feats = self.text_vectorizer.transform(corpus)

        tags = self._prepare_tags(df)
        tag_feats = csr_matrix(self.tag_binarizer.transform(tags)) * 2.0  # Weight tags strongly

        diffs = self._prepare_diff(df)
        diff_feats = self.diff_encoder.transform(diffs) * 1.5

        # Stack multi-modal representations and normalize
        combined = hstack([text_feats, tag_feats, diff_feats]).tocsr()
        normalized = normalize(combined, norm="l2")
        return normalized

    def transform_single(self, title: str, description: str, topic_tags: List[str], difficulty: str) -> csr_matrix:
        single_df = pd.DataFrame([{
            "task_id": title,
            "problem_description": description,
            "topic_tags": topic_tags,
            "difficulty": difficulty,
            "starter_code": ""
        }])
        return self.transform(single_df)


class DifficultyClassifier:
    """Predicts difficulty level (Easy, Medium, Hard) from problem text."""
    def __init__(self):
        self.model = LogisticRegression(C=1.5, max_iter=1000, class_weight="balanced", random_state=42)
        self.is_fitted = False

    def fit(self, text_vectors: csr_matrix, y_diff: np.ndarray):
        self.model.fit(text_vectors, y_diff)
        self.is_fitted = True
        return self

    def predict(self, text_vector: csr_matrix) -> Tuple[str, float]:
        if not self.is_fitted:
            return "Medium", 0.5
        probs = self.model.predict_proba(text_vector)[0]
        max_idx = np.argmax(probs)
        label = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        return str(label), round(confidence, 3)


class TopicClassifier:
    """Predicts multi-label algorithmic topic tags from problem text."""
    def __init__(self, top_topics: int = 30):
        self.top_topics = top_topics
        self.models: Dict[str, LogisticRegression] = {}
        self.target_topics: List[str] = []
        self.is_fitted = False

    def fit(self, text_vectors: csr_matrix, tag_lists: List[List[str]]):
        counts = defaultdict(int)
        for tags in tag_lists:
            for t in tags:
                counts[t] += 1

        self.target_topics = [t for t, c in sorted(counts.items(), key=lambda x: x[1], reverse=True) if c >= 25][:self.top_topics]
        
        for topic in self.target_topics:
            y = np.array([1 if topic in tags else 0 for tags in tag_lists])
            clf = LogisticRegression(C=2.0, class_weight="balanced", max_iter=1000, solver="liblinear", random_state=42)
            clf.fit(text_vectors, y)
            self.models[topic] = clf

        self.is_fitted = True
        return self

    def predict(self, text_vector: csr_matrix, top_k: int = 4) -> List[str]:
        if not self.is_fitted:
            return ["Array", "Algorithms"]
        scores = []
        for topic in self.target_topics:
            clf = self.models.get(topic)
            if clf is not None:
                prob = float(clf.predict_proba(text_vector)[0, 1])
                scores.append((topic, prob))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return [t for t, p in scores[:top_k] if p >= 0.35] or ["Array", "Algorithms"]


class CompanyClassifier:
    """
    Multi-label supervised company classifier + company interview centroid matcher.
    """
    def __init__(self, top_n_companies: int = 80, min_company_problems: int = 15):
        self.top_n_companies = top_n_companies
        self.min_company_problems = min_company_problems
        self.models: Dict[str, LogisticRegression] = {}
        self.target_companies: List[str] = []
        self.company_centroids: Dict[str, np.ndarray] = {}
        self.company_freq_weights: Dict[str, float] = {}
        self.is_fitted = False

    def fit(self, X: csr_matrix, df: pd.DataFrame):
        company_counts = defaultdict(int)
        for _, row in df.iterrows():
            comps = row.get("companies", [])
            if isinstance(comps, (list, np.ndarray)):
                for c in comps:
                    company_counts[c] += 1
            elif isinstance(comps, str) and comps.strip():
                for c in comps.split(";"):
                    company_counts[c.strip()] += 1

        sorted_comps = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
        self.target_companies = [
            c for c, count in sorted_comps
            if count >= self.min_company_problems
        ][:self.top_n_companies]

        print(f"Training multi-label classifiers for top {len(self.target_companies)} companies...")

        for company in self.target_companies:
            y = np.array([
                1 if (isinstance(comps, (list, np.ndarray)) and company in comps)
                or (isinstance(comps, str) and company in [c.strip() for c in comps.split(";")])
                else 0
                for comps in df["companies"]
            ])

            if y.sum() < 5:
                continue

            clf = LogisticRegression(
                C=2.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
                solver="liblinear"
            )
            clf.fit(X, y)
            self.models[company] = clf

            pos_indices = np.where(y == 1)[0]
            pos_vectors = X[pos_indices].toarray()
            
            weights = []
            for idx in pos_indices:
                row = df.iloc[idx]
                details = row.get("company_details", {})
                if isinstance(details, str):
                    try: details = json.loads(details)
                    except: details = {}
                comp_stat = details.get(company, {}) if isinstance(details, dict) else {}
                freq = comp_stat.get("max_frequency", 1.0)
                weights.append(max(float(freq), 0.5))
                
            weights = np.array(weights)[:, np.newaxis]
            weighted_centroid = np.sum(pos_vectors * weights, axis=0) / np.sum(weights)
            centroid_norm = np.linalg.norm(weighted_centroid)
            if centroid_norm > 0:
                weighted_centroid = weighted_centroid / centroid_norm
            self.company_centroids[company] = weighted_centroid
            self.company_freq_weights[company] = float(np.mean(weights))

        self.is_fitted = True
        return self

    def predict_companies(
        self,
        X_vec: csr_matrix,
        top_k: int = 10,
        feature_extractor: Optional[LeetCodeFeatureExtractor] = None,
        query_text: str = ""
    ) -> List[Dict[str, Any]]:
        if not self.is_fitted:
            raise ValueError("Company classifier is not fitted.")

        x_dense = X_vec.toarray()[0]
        results = []

        for company in self.target_companies:
            clf = self.models.get(company)
            centroid = self.company_centroids.get(company)

            prob = float(clf.predict_proba(X_vec)[0, 1]) if clf is not None else 0.0

            if centroid is not None:
                cosine_sim = float(np.dot(x_dense, centroid))
                affinity = max(0.0, min(1.0, (cosine_sim + 0.1) * 1.3))
            else:
                affinity = 0.0

            combined_score = (0.55 * prob) + (0.45 * affinity)
            confidence_pct = round(min(99.0, max(5.0, combined_score * 100)), 1)

            results.append({
                "company": company,
                "confidence_score": confidence_pct,
                "classifier_prob": round(prob, 3),
                "centroid_affinity": round(affinity, 3),
            })

        results = sorted(results, key=lambda x: x["confidence_score"], reverse=True)[:top_k]

        for item in results:
            comp = item["company"]
            conf = item["confidence_score"]
            if conf >= 75:
                verdict = f"High probability core question for {comp.title()} interviews."
            elif conf >= 50:
                verdict = f"Matches {comp.title()}'s preferred algorithmic style."
            else:
                verdict = f"Moderate archetype overlap with {comp.title()} question bank."
            item["rationale"] = verdict

        return results


def compute_difficulty_tier(difficulty: str, topic_tags: Any, description: str = "") -> str:
    """Classifies problems into 5 granular difficulty bands."""
    diff = str(difficulty).strip().capitalize() if difficulty else "Medium"
    
    tags = []
    if isinstance(topic_tags, (list, np.ndarray)):
        tags = [str(t) for t in topic_tags]
    elif isinstance(topic_tags, str) and topic_tags.strip():
        tags = [t.strip() for t in topic_tags.split(";")]

    hard_tags = {"Dynamic Programming", "Graph", "Segment Tree", "Binary Indexed Tree", "Trie", "Bitmask", "Suffix Array", "Eulerian Circuit"}
    easy_tags = {"Array", "Math", "Hash Table", "String", "Simulation"}
    desc_len = len(str(description))

    if diff == "Easy":
        if any(t in hard_tags for t in tags) or desc_len > 1100:
            return "Easy-Medium"
        return "Easy"
    elif diff == "Medium":
        if any(t in hard_tags for t in tags) or desc_len > 1500:
            return "Medium-Hard"
        elif all(t in easy_tags for t in tags) and desc_len < 650:
            return "Easy-Medium"
        return "Medium"
    elif diff == "Hard":
        if any(t in {"Math", "Greedy", "Array"} for t in tags) and not any(t in hard_tags for t in tags) and desc_len < 850:
            return "Medium-Hard"
        return "Hard"
    return "Medium"


def clean_problem_text_for_nlp(text: str) -> str:
    """
    Strips HTML, markdown links/images, boilerplate headers (Example 1, Constraints),
    while preserving algorithmic clues, numbers, and mathematical conditions.
    """
    if not text or pd.isna(text):
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"(example\s*\d+:|constraints:|input:|output:|explanation:|follow\s*up:)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[^\w\s\-\+\*\/\<\>\=\$\%]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


ARCHETYPES_TAXONOMY: Dict[int, Dict[str, Any]] = {
    0: {
        "id": 0,
        "name": "Two Pointers",
        "paradigm": "Linear Pointer Patterns",
        "phase": "Phase 1: Linear Pointer Mechanics (Weeks 1-2)",
        "description": "Converging or diverging pointers on sorted arrays or strings for pair matching, palindrome validation, and container optimization.",
        "invariant": "left < right with monotonic convergence condition.",
        "complexity": "Time: O(N), Space: O(1)",
        "canonical_examples": ["two-sum-ii-input-array-is-sorted", "3sum", "container-with-most-water", "trapping-rain-water"],
        "keywords": ["two pointer", "opposite ends", "converge", "palindrome", "sorted pair", "left right", "partition array"],
        "gfg_topic": "Two Pointers Technique",
        "gfg_url": "https://www.geeksforgeeks.org/two-pointers-technique/"
    },
    1: {
        "id": 1,
        "name": "Sliding Window",
        "paradigm": "Linear Pointer Patterns",
        "phase": "Phase 1: Linear Pointer Mechanics (Weeks 1-2)",
        "description": "Expanding/shrinking contiguous range to optimize subarray/substring bounds in single-pass linear time.",
        "invariant": "Fixed: [R - K + 1 ... R] | Variable: expand R, while invalid shrink L.",
        "complexity": "Time: O(N), Space: O(K) or O(1)",
        "canonical_examples": ["maximum-average-subarray-i", "longest-substring-without-repeating-characters", "max-consecutive-ones-iii", "minimum-window-substring", "subarrays-with-k-different-integers"],
        "keywords": ["sliding window", "subarray", "substring", "contiguous", "longest substring", "at most k", "minimum window"],
        "gfg_topic": "Window Sliding Technique",
        "gfg_url": "https://www.geeksforgeeks.org/window-sliding-technique/"
    },
    2: {
        "id": 2,
        "name": "Prefix Sum & Difference Array",
        "paradigm": "Linear Pointer Patterns",
        "phase": "Phase 1: Linear Pointer Mechanics (Weeks 1-2)",
        "description": "O(1) range sum queries, prefix frequency counters, or range update increments via cumulative arrays.",
        "invariant": "Sum(i...j) = Prefix[j+1] - Prefix[i] | Diff[L]+=V, Diff[R+1]-=V",
        "complexity": "Time: O(1) query / O(N) precompute, Space: O(N)",
        "canonical_examples": ["subarray-sum-equals-k", "range-sum-query-immutable", "corporate-flight-bookings", "product-of-array-except-self"],
        "keywords": ["prefix sum", "cumulative", "difference array", "range sum", "subarray sum", "prefix", "running sum"],
        "gfg_topic": "Prefix Sum Array & Applications",
        "gfg_url": "https://www.geeksforgeeks.org/prefix-sum-array-implementation-applications-competitive-programming/"
    },
    3: {
        "id": 3,
        "name": "Fast & Slow Pointers",
        "paradigm": "Linear Pointer Patterns",
        "phase": "Phase 1: Linear Pointer Mechanics (Weeks 1-2)",
        "description": "Two pointers moving at different speeds (1x, 2x) to detect cycles, find linked list midpoints, or discover repeating state sequences.",
        "invariant": "slow moves 1 step, fast moves 2 steps. Intersection implies cycle.",
        "complexity": "Time: O(N), Space: O(1)",
        "canonical_examples": ["linked-list-cycle", "linked-list-cycle-ii", "find-the-duplicate-number", "happy-number", "middle-of-the-linked-list"],
        "keywords": ["fast slow", "cycle", "tortoise hare", "floyd", "middle linked list", "linked list cycle", "happy number"],
        "gfg_topic": "Floyd's Cycle Finding Algorithm",
        "gfg_url": "https://www.geeksforgeeks.org/floyds-cycle-finding-algorithm/"
    },
    4: {
        "id": 4,
        "name": "Monotonic Stack & Queue",
        "paradigm": "Linear Structures & Specialized Memory",
        "phase": "Phase 2: Core Linear Data Structures (Weeks 3-4)",
        "description": "Maintaining a strictly increasing/decreasing sequence to find next greater/smaller element in O(N) amortized time.",
        "invariant": "Stack elements maintain strict monotonicity. Pop elements that violate invariant.",
        "complexity": "Time: O(N) amortized, Space: O(N)",
        "canonical_examples": ["daily-temperatures", "next-greater-element-i", "largest-rectangle-in-histogram", "sliding-window-maximum", "online-stock-span"],
        "keywords": ["monotonic stack", "next greater", "next smaller", "histogram", "monotonic queue", "temperatures", "stock span"],
        "gfg_topic": "Next Greater Element & Monotonic Stack",
        "gfg_url": "https://www.geeksforgeeks.org/next-greater-element/"
    },
    5: {
        "id": 5,
        "name": "In-Place Manipulation & Cyclic Sort",
        "paradigm": "Linear Structures & Specialized Memory",
        "phase": "Phase 2: Core Linear Data Structures (Weeks 3-4)",
        "description": "Swapping elements into their correct 1-indexed position in O(N) time and O(1) auxiliary space.",
        "invariant": "while nums[i] != nums[nums[i]-1]: swap(i, nums[i]-1)",
        "complexity": "Time: O(N), Space: O(1)",
        "canonical_examples": ["first-missing-positive", "missing-number", "find-all-duplicates-in-an-array", "set-mismatch"],
        "keywords": ["cyclic sort", "first missing", "in-place swap", "1 to n", "duplicate number", "missing number", "in-place"],
        "gfg_topic": "Cycle Sort Algorithm",
        "gfg_url": "https://www.geeksforgeeks.org/cycle-sort/"
    },
    6: {
        "id": 6,
        "name": "Heaps & Priority Queues",
        "paradigm": "Linear Structures & Specialized Memory",
        "phase": "Phase 2: Core Linear Data Structures (Weeks 3-4)",
        "description": "Tracking top K elements, running medians, or multi-stream merges via binary heap invariants.",
        "invariant": "Min-heap / Max-heap root invariant. Top-K maintains heap of size K.",
        "complexity": "Time: O(N log K), Space: O(K)",
        "canonical_examples": ["kth-largest-element-in-an-array", "top-k-frequent-elements", "find-median-from-data-stream", "merge-k-sorted-lists", "task-scheduler"],
        "keywords": ["heap", "priority queue", "kth largest", "top k", "median stream", "min heap", "max heap", "priority"],
        "gfg_topic": "Heap Data Structure & Priority Queue",
        "gfg_url": "https://www.geeksforgeeks.org/heap-data-structure/"
    },
    7: {
        "id": 7,
        "name": "Trie & Hash Mechanics",
        "paradigm": "Linear Structures & Specialized Memory",
        "phase": "Phase 2: Core Linear Data Structures (Weeks 3-4)",
        "description": "Prefix matching, frequency counting, and custom rolling hashes across large strings and vocabularies.",
        "invariant": "Prefix tree node transition on char. Rolling hash: H = (H * B + C) % M",
        "complexity": "Time: O(L) per word, Space: O(N * L * Alphabet)",
        "canonical_examples": ["implement-trie-prefix-tree", "word-search-ii", "longest-duplicate-substring", "group-anagrams", "design-add-and-search-words-data-structure"],
        "keywords": ["trie", "prefix tree", "hash table", "rolling hash", "rabin karp", "anagram", "hash map", "frequency map"],
        "gfg_topic": "Trie Insert and Search",
        "gfg_url": "https://www.geeksforgeeks.org/trie-insert-and-search/"
    },
    8: {
        "id": 8,
        "name": "Tree & Tree DP",
        "paradigm": "Tree, Graph & Search Space Traversal",
        "phase": "Phase 3: Hierarchical Structures & Search Space (Weeks 5-6)",
        "description": "Recursion, structural traversals (In/Pre/Post/Level-order), and bottom-up tree state propagation.",
        "invariant": "State(node) = f(State(node.left), State(node.right))",
        "complexity": "Time: O(N), Space: O(H) where H is tree height",
        "canonical_examples": ["lowest-common-ancestor-of-a-binary-tree", "binary-tree-maximum-path-sum", "diameter-of-binary-tree", "house-robber-iii", "serialize-and-deserialize-binary-tree"],
        "keywords": ["tree", "binary tree", "bst", "lowest common ancestor", "tree dp", "traversal", "postorder", "inorder", "preorder"],
        "gfg_topic": "Binary Tree & Tree Traversals",
        "gfg_url": "https://www.geeksforgeeks.org/binary-tree-data-structure/"
    },
    9: {
        "id": 9,
        "name": "Graph Traversal & Matrix BFS/DFS",
        "paradigm": "Tree, Graph & Search Space Traversal",
        "phase": "Phase 4: Graph Theory & Combinatorial Search (Weeks 7-8)",
        "description": "Connected components, flood fill, shortest path in unweighted grids, multi-source BFS, and Dijkstra's algorithm.",
        "invariant": "Queue tracks frontier level-by-level; Visited set prevents infinite cycles.",
        "complexity": "Time: O(V + E) or O(R * C), Space: O(V + E)",
        "canonical_examples": ["number-of-islands", "rotting-oranges", "pacific-atlantic-water-flow", "word-ladder", "clone-graph", "cheapest-flights-within-k-stops"],
        "keywords": ["graph", "bfs", "dfs", "matrix", "grid", "islands", "shortest path", "flood fill", "dijkstra", "bipartite"],
        "gfg_topic": "Graph Data Structure & BFS/DFS",
        "gfg_url": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/"
    },
    10: {
        "id": 10,
        "name": "DSU & Topological Sort",
        "paradigm": "Tree, Graph & Search Space Traversal",
        "phase": "Phase 4: Graph Theory & Combinatorial Search (Weeks 7-8)",
        "description": "Cycle detection, dynamic connectivity (Union-Find), and dependency ordering for DAGs.",
        "invariant": "DSU: Find(x) == Find(y) | Topo: indegree == 0 nodes enter queue first.",
        "complexity": "Time: O((V+E) * alpha(V)) or O(V+E), Space: O(V+E)",
        "canonical_examples": ["course-schedule", "course-schedule-ii", "redundant-connection", "graph-valid-tree", "accounts-merge", "number-of-provinces"],
        "keywords": ["union find", "dsu", "topological sort", "indegree", "cycle detection", "disjoint set", "course schedule", "connected components"],
        "gfg_topic": "Disjoint Set Union (Union-Find)",
        "gfg_url": "https://www.geeksforgeeks.org/disjoint-set-data-structures/"
    },
    11: {
        "id": 11,
        "name": "Backtracking & Combinatorial Search",
        "paradigm": "Tree, Graph & Search Space Traversal",
        "phase": "Phase 4: Graph Theory & Combinatorial Search (Weeks 7-8)",
        "description": "Systematically exploring state options via DFS decision trees with constraint pruning.",
        "invariant": "Choose -> Explore -> Unchoose (backtrack state restore)",
        "complexity": "Time: O(K^N) or O(N!), Space: O(N) recursion stack",
        "canonical_examples": ["subsets", "permutations", "n-queens", "sudoku-solver", "word-search", "combination-sum", "palindrome-partitioning"],
        "keywords": ["backtracking", "subsets", "permutations", "combinations", "n queens", "pruning", "dfs search", "sudoku", "combination sum"],
        "gfg_topic": "Backtracking Algorithms",
        "gfg_url": "https://www.geeksforgeeks.org/backtracking-algorithms/"
    },
    12: {
        "id": 12,
        "name": "Binary Search on Solution Space",
        "paradigm": "Optimization & State Space Paradigms",
        "phase": "Phase 3: Hierarchical Structures & Search Space (Weeks 5-6)",
        "description": "Searching for optimal boundary in monotonic decision spaces f(x) -> {True, False}.",
        "invariant": "low <= high; monotonic predicate condition divides search space.",
        "complexity": "Time: O(N log(SearchSpace)), Space: O(1)",
        "canonical_examples": ["koko-eating-bananas", "capacity-to-ship-packages-within-d-days", "split-array-largest-sum", "find-first-and-last-position-of-element-in-sorted-array", "search-in-rotated-sorted-array"],
        "keywords": ["binary search", "search space", "monotonic", "koko", "capacity", "optimal boundary", "bisect", "rotated sorted"],
        "gfg_topic": "Binary Search Algorithms",
        "gfg_url": "https://www.geeksforgeeks.org/binary-search/"
    },
    13: {
        "id": 13,
        "name": "Dynamic Programming",
        "paradigm": "Optimization & State Space Paradigms",
        "phase": "Phase 5: Advanced Optimization & State Transitions (Weeks 9-11)",
        "description": "Overlapping subproblems & optimal substructure (1D, 2D, Grid, Interval, and Bitmask DP).",
        "invariant": "DP[state] = optimal_transition(DP[sub_states])",
        "complexity": "Time: O(States * Transitions), Space: O(States)",
        "canonical_examples": ["climbing-stairs", "house-robber", "longest-common-subsequence", "coin-change", "burst-balloons", "edit-distance", "target-sum"],
        "keywords": ["dynamic programming", "memoization", "knapsack", "subsequence", "interval dp", "bitmask dp", "state transition", "dp", "longest common"],
        "gfg_topic": "Dynamic Programming (DP)",
        "gfg_url": "https://www.geeksforgeeks.org/dynamic-programming/"
    },
    14: {
        "id": 14,
        "name": "Greedy & Interval Scheduling",
        "paradigm": "Optimization & State Space Paradigms",
        "phase": "Phase 5: Advanced Optimization & State Transitions (Weeks 9-11)",
        "description": "Making locally optimal choices and merging/sorting overlapping intervals.",
        "invariant": "Sort by start/end time. Greedy choice property guarantees global optimum.",
        "complexity": "Time: O(N log N), Space: O(1) or O(N)",
        "canonical_examples": ["merge-intervals", "non-overlapping-intervals", "task-scheduler", "gas-station", "jump-game", "minimum-number-of-arrows-to-burst-balloons"],
        "keywords": ["greedy", "intervals", "merge intervals", "interval scheduling", "locally optimal", "jump game", "gas station", "interval"],
        "gfg_topic": "Greedy Algorithms",
        "gfg_url": "https://www.geeksforgeeks.org/greedy-algorithms/"
    }
}

CORE_PARADIGMS = [
    "Linear Pointer Patterns",
    "Linear Structures & Specialized Memory",
    "Tree, Graph & Search Space Traversal",
    "Optimization & State Space Paradigms"
]

ROADMAP_PHASES = [
    {
        "phase": "Phase 1: Linear Traversals & Pointer Mechanics",
        "weeks": "Weeks 1–2",
        "archetypes": [0, 1, 2, 3],
        "goal": "Shift from O(N²) brute force to O(N) single-pass time complexity.",
        "mechanics": "Converging/diverging bounds, range queries, and subarray optimization.",
        "gfg_links": [
            {"title": "GFG Array Data Structure", "url": "https://www.geeksforgeeks.org/array-data-structure/"},
            {"title": "GFG Searching Algorithms", "url": "https://www.geeksforgeeks.org/searching-algorithms/"}
        ]
    },
    {
        "phase": "Phase 2: Core Linear Data Structures & Memory",
        "weeks": "Weeks 3–4",
        "archetypes": [4, 5, 6, 7],
        "goal": "Solve order-dependent and range-query problems efficiently without extra re-sorting.",
        "mechanics": "Tracking next greater elements, O(1) lookups, and top-K elements.",
        "gfg_links": [
            {"title": "GFG Stack Data Structure", "url": "https://www.geeksforgeeks.org/stack-data-structure/"},
            {"title": "GFG Hashing Data Structure", "url": "https://www.geeksforgeeks.org/hashing-data-structure/"}
        ]
    },
    {
        "phase": "Phase 3: Hierarchical Data & Search Space",
        "weeks": "Weeks 5–6",
        "archetypes": [8, 12],
        "goal": "Master divide-and-conquer logic, tree recursion, and monotonic answer spaces.",
        "mechanics": "In/Pre/Post-order traversals, lowest common ancestors, and monotonic decision boundaries.",
        "gfg_links": [
            {"title": "GFG Binary Tree", "url": "https://www.geeksforgeeks.org/binary-tree-data-structure/"},
            {"title": "GFG Binary Search", "url": "https://www.geeksforgeeks.org/binary-search/"}
        ]
    },
    {
        "phase": "Phase 4: Graph Theory & Combinatorial Search",
        "weeks": "Weeks 7–8",
        "archetypes": [9, 10, 11],
        "goal": "Model real-world dependency networks and state-space tree prunings.",
        "mechanics": "Shortest paths, connected components, dependency graph modeling, and combinatorial DFS.",
        "gfg_links": [
            {"title": "GFG Graph Data Structure", "url": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/"},
            {"title": "GFG Backtracking Algorithms", "url": "https://www.geeksforgeeks.org/backtracking-algorithms/"}
        ]
    },
    {
        "phase": "Phase 5: Advanced Optimization & State Transitions",
        "weeks": "Weeks 9–11",
        "archetypes": [13, 14],
        "goal": "Recognize state transition equations and convert exponential recursion into polynomial time.",
        "mechanics": "Overlapping subproblems, state transitions, and interval scheduling.",
        "gfg_links": [
            {"title": "GFG Dynamic Programming", "url": "https://www.geeksforgeeks.org/dynamic-programming/"},
            {"title": "GFG Greedy Algorithms", "url": "https://www.geeksforgeeks.org/greedy-algorithms/"}
        ]
    },
    {
        "phase": "Phase 6: Composite Patterns & Advanced Structures",
        "weeks": "Weeks 12+",
        "archetypes": [6, 7, 13],
        "goal": "Handle edge cases under strict O(N log N) or O(1) space constraints.",
        "mechanics": "Bitmask DP, custom Trie dictionaries, and multi-paradigm combinations.",
        "gfg_links": [
            {"title": "GFG Bitmasking and DP", "url": "https://www.geeksforgeeks.org/bitmasking-and-dynamic-programming/"},
            {"title": "GFG Segment Tree", "url": "https://www.geeksforgeeks.org/segment-tree-data-structure/"}
        ]
    }
]


class MultiLabelPatternClassifier:
    """
    NLP Multi-Label Pattern Classifier.
    Predicts multiple overlapping DSA patterns (e.g. Dynamic Programming, Sliding Window)
    from unannotated raw problem descriptions using BCE-calibrated probabilities.
    """
    def __init__(self, n_archetypes: int = 15):
        self.n_archetypes = n_archetypes
        self.vectorizer = TfidfVectorizer(
            max_features=6000,
            sublinear_tf=True,
            ngram_range=(1, 3),
            stop_words="english",
            min_df=2
        )
        self.classifiers = [
            LogisticRegression(class_weight="balanced", max_iter=400, random_state=42 + i, C=1.5)
            for i in range(n_archetypes)
        ]
        self.is_fitted = False

    def fit(self, texts: List[str], multi_hot_labels: np.ndarray):
        X_vec = self.vectorizer.fit_transform([clean_problem_text_for_nlp(t) for t in texts])
        for i in range(self.n_archetypes):
            y_i = multi_hot_labels[:, i]
            if len(np.unique(y_i)) > 1:
                self.classifiers[i].fit(X_vec, y_i)
        self.is_fitted = True
        return self

    def predict_patterns(self, text: str, threshold: float = 0.25, top_k: int = 5) -> List[Dict[str, Any]]:
        cleaned = clean_problem_text_for_nlp(text)
        if not self.is_fitted:
            # Fallback heuristic prediction
            pred_id = classify_problem_to_archetype({"problem_description": text, "title": text})
            arch = ARCHETYPES_TAXONOMY.get(pred_id, ARCHETYPES_TAXONOMY[0])
            return [{
                "archetype_id": pred_id,
                "name": arch["name"],
                "paradigm": arch["paradigm"],
                "probability": 0.85,
                "confidence_pct": 85.0,
                "invariant": arch["invariant"],
                "complexity": arch["complexity"],
                "gfg_topic": arch["gfg_topic"],
                "gfg_url": arch["gfg_url"]
            }]

        X_vec = self.vectorizer.transform([cleaned])
        scored = []
        for i in range(self.n_archetypes):
            arch = ARCHETYPES_TAXONOMY[i]
            prob = 0.0
            if hasattr(self.classifiers[i], "predict_proba"):
                prob = float(self.classifiers[i].predict_proba(X_vec)[0, 1])
            
            # Boost canonical keyword detections
            for kw in arch.get("keywords", []):
                if kw in cleaned:
                    prob = min(0.98, prob + 0.20)

            scored.append({
                "archetype_id": i,
                "name": arch["name"],
                "paradigm": arch["paradigm"],
                "probability": round(prob, 4),
                "confidence_pct": round(prob * 100, 1),
                "invariant": arch["invariant"],
                "complexity": arch["complexity"],
                "gfg_topic": arch["gfg_topic"],
                "gfg_url": arch["gfg_url"],
                "canonical_examples": arch["canonical_examples"]
            })

        scored.sort(key=lambda x: x["probability"], reverse=True)
        # Filter by threshold or return top_k
        filtered = [s for s in scored if s["probability"] >= threshold]
        return filtered[:top_k] if filtered else scored[:top_k]



def classify_problem_to_archetype(row) -> int:
    """Classifies a problem into one of the 15 mutually exclusive archetypes."""
    task_id = str(row.get("task_id", "")).lower()
    title = str(row.get("title", "")).lower()
    desc = str(row.get("problem_description", "")).lower()
    
    tags = row.get("topic_tags", [])
    if isinstance(tags, (list, np.ndarray)):
        tag_str = " ".join([str(t).lower() for t in tags])
    elif isinstance(tags, str):
        tag_str = tags.lower()
    else:
        tag_str = ""

    full_text = f"{task_id} {title} {tag_str} {desc[:400]}"

    # Exact Canonical Priority Rules
    if any(k in full_text for k in ["trie", "prefix tree", "rolling hash", "rabin karp"]):
        return 7
    if any(k in full_text for k in ["union find", "disjoint set", "topological sort", "course schedule", "bipartite"]):
        return 10
    if any(k in full_text for k in ["monotonic stack", "daily temperatures", "next greater", "next smaller", "largest rectangle in histogram"]):
        return 4
    if any(k in full_text for k in ["cyclic sort", "first missing positive", "missing number", "set mismatch", "find all numbers disappeared", "find all duplicates in an array"]):
        return 5
    if any(k in full_text for k in ["fast slow", "linked list cycle", "tortoise hare", "middle of the linked list", "happy number", "remove nth node from end", "reorder list"]):
        return 3
    if any(k in full_text for k in ["sliding window", "longest substring without repeating", "minimum window substring", "subarrays with k different", "longest repeating character replacement"]):
        return 1
    if any(k in full_text for k in ["prefix sum", "difference array", "subarray sum equals", "range sum query", "product of array except self"]):
        return 2
    if any(k in full_text for k in ["binary search", "search in rotated", "koko eating", "capacity to ship", "split array largest sum", "find peak element"]):
        return 12
    if any(k in full_text for k in ["heap", "priority queue", "kth largest", "top k frequent", "median from data stream", "merge k sorted"]):
        return 6
    if any(k in full_text for k in ["binary tree", "binary search tree", "lowest common ancestor", "serialize and deserialize", "tree dp", "diameter of binary tree"]):
        return 8
    if any(k in full_text for k in ["backtracking", "n-queens", "sudoku", "permutations", "subsets", "combination sum", "word search"]):
        return 11
    if any(k in full_text for k in ["dynamic programming", "longest common subsequence", "coin change", "house robber", "edit distance", "burst balloons", "knapsack"]):
        return 13
    if any(k in full_text for k in ["interval", "merge intervals", "task scheduler", "gas station", "jump game", "non-overlapping"]):
        return 14
    if any(k in full_text for k in ["graph", "bfs", "dfs", "matrix", "islands", "shortest path", "rotting oranges", "flood fill"]):
        return 9
    if any(k in full_text for k in ["two pointer", "3sum", "container with most water", "two sum ii", "trapping rain water", "valid palindrome"]):
        return 0

    # Secondary Topic Tag Matches
    if "dynamic programming" in tag_str or "memoization" in tag_str:
        return 13
    if "tree" in tag_str or "binary tree" in tag_str or "binary search tree" in tag_str:
        return 8
    if "graph" in tag_str or "breadth-first search" in tag_str or "depth-first search" in tag_str or "matrix" in tag_str:
        return 9
    if "binary search" in tag_str:
        return 12
    if "heap (priority queue)" in tag_str:
        return 6
    if "sliding window" in tag_str:
        return 1
    if "prefix sum" in tag_str:
        return 2
    if "linked list" in tag_str:
        return 3
    if "stack" in tag_str or "monotonic stack" in tag_str:
        return 4
    if "two pointers" in tag_str:
        return 0
    if "greedy" in tag_str:
        return 14
    if "backtracking" in tag_str:
        return 11
    if "trie" in tag_str:
        return 7
    if "union find" in tag_str or "topological sort" in tag_str:
        return 10

    return 0


class ProblemClusterEngine:
    """
    Unified 15-Archetype Taxonomy Engine (Zero Duplication)
    Classifies 2,870+ problems into 15 algorithmic archetypes across 4 Core Paradigms,
    stratified into 5 Difficulty Tiers with sub-millisecond NearestNeighbors similarity lookup.
    """
    def __init__(self, n_clusters: int = 15):
        self.n_clusters = 15
        self.nn_index = NearestNeighbors(metric="cosine", algorithm="brute")
        self.cluster_labels: Dict[int, str] = {}
        self.cluster_summaries: Dict[int, Dict[str, Any]] = {}
        self.archetypes_taxonomy = ARCHETYPES_TAXONOMY
        self.core_paradigms = CORE_PARADIGMS
        self.roadmap_phases = ROADMAP_PHASES
        self.is_fitted = False

    def fit(self, X: csr_matrix, df: pd.DataFrame, feature_extractor: LeetCodeFeatureExtractor):
        print(f"Mapping {X.shape[0]} LeetCode problems into Unified 15-Archetype Taxonomy...")
        
        # 1. Classify each problem into 1 of 15 Archetypes
        cluster_ids = df.apply(classify_problem_to_archetype, axis=1).values
        df["cluster_id"] = cluster_ids
        
        # 2. Assign 5-Tier Difficulty Stratification
        df["difficulty_tier"] = df.apply(
            lambda row: compute_difficulty_tier(row.get("difficulty"), row.get("topic_tags"), row.get("problem_description", "")),
            axis=1
        )
        
        # 3. Fit Nearest Neighbors index on all vectors
        self.nn_index.fit(X)

        terms = np.array(feature_extractor.text_vectorizer.get_feature_names_out())
        
        for c_id, arch in self.archetypes_taxonomy.items():
            c_members = df[df["cluster_id"] == c_id]
            size = len(c_members)
            
            # Extract Top Tags
            all_tags = []
            for tags in c_members["topic_tags"]:
                if isinstance(tags, (list, np.ndarray)):
                    all_tags.extend(tags)
                elif isinstance(tags, str) and tags.strip():
                    all_tags.extend([t.strip() for t in tags.split(";")])
            
            tag_counts = pd.Series(all_tags).value_counts()
            top_tags = tag_counts.head(5).index.tolist() if not tag_counts.empty else ["Algorithms"]
            
            # 5-Tier Breakdown
            tier_dist = c_members["difficulty_tier"].value_counts().to_dict()
            tier_breakdown = {
                "Easy": int(tier_dist.get("Easy", 0)),
                "Easy-Medium": int(tier_dist.get("Easy-Medium", 0)),
                "Medium": int(tier_dist.get("Medium", 0)),
                "Medium-Hard": int(tier_dist.get("Medium-Hard", 0)),
                "Hard": int(tier_dist.get("Hard", 0))
            }
            diff_dist = c_members["difficulty"].value_counts().to_dict()

            self.cluster_labels[c_id] = arch["name"]

            # Group Problems by 5 Difficulty Tiers for direct UI linking
            problems_by_tier = {"Easy": [], "Easy-Medium": [], "Medium": [], "Medium-Hard": [], "Hard": []}
            for _, prob in c_members.iterrows():
                tier = prob.get("difficulty_tier", "Medium")
                if tier not in problems_by_tier:
                    tier = "Medium"
                prob_tags = prob["topic_tags"] if isinstance(prob["topic_tags"], list) else []
                prob_comps = prob["companies"] if isinstance(prob["companies"], list) else []
                problems_by_tier[tier].append({
                    "task_id": prob["task_id"],
                    "question_id": int(prob["question_id"]) if pd.notna(prob.get("question_id")) else None,
                    "title": prob.get("title") or prob["task_id"].replace("-", " ").title(),
                    "difficulty": prob["difficulty"],
                    "difficulty_tier": tier,
                    "topic_tags": prob_tags[:3],
                    "companies": prob_comps[:4],
                    "companies_count": int(prob.get("companies_count", len(prob_comps))),
                    "leetcode_url": f"https://leetcode.com/problems/{prob['task_id']}/"
                })

            self.cluster_summaries[c_id] = {
                "cluster_id": c_id,
                "title": arch["name"],
                "archetype_name": arch["name"],
                "paradigm": arch["paradigm"],
                "phase": arch["phase"],
                "description": arch["description"],
                "invariant": arch["invariant"],
                "complexity": arch["complexity"],
                "canonical_examples": arch["canonical_examples"],
                "size": size,
                "problem_count": size,
                "top_tags": top_tags,
                "top_keywords": arch["keywords"],
                "difficulty_distribution": diff_dist,
                "tier_distribution": tier_breakdown,
                "problems_by_tier": problems_by_tier,
                "sample_problems": c_members["task_id"].head(6).tolist()
            }

        self.is_fitted = True
        return self

    def reindex(self, X_all: csr_matrix):
        """Re-fits NearestNeighbors on updated dataset."""
        self.nn_index = NearestNeighbors(metric="cosine", algorithm="brute")
        self.nn_index.fit(X_all)

    def get_similar_problems(
        self,
        X_vec: csr_matrix,
        top_k: int = 10,
        exclude_indices: Optional[set] = None
    ) -> List[Tuple[int, float]]:
        if not self.is_fitted:
            raise ValueError("Cluster engine is not fitted.")

        k_search = min(top_k + (len(exclude_indices) if exclude_indices else 0) + 10, self.nn_index.n_samples_fit_)
        distances, indices = self.nn_index.kneighbors(X_vec, n_neighbors=k_search)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if exclude_indices and idx in exclude_indices:
                continue
            sim = round(max(0.0, min(1.0, 1.0 - float(dist))), 4)
            results.append((int(idx), sim))
            if len(results) >= top_k:
                break

        return results


class LeetCodeIntelligenceEngine:
    """
    Unified Intelligence & Auto-Classification Engine.
    """
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.feature_extractor = LeetCodeFeatureExtractor()
        self.difficulty_classifier = DifficultyClassifier()
        self.topic_classifier = TopicClassifier()
        self.company_classifier = CompanyClassifier()
        self.cluster_engine = ProblemClusterEngine()
        self.pattern_classifier = MultiLabelPatternClassifier(n_archetypes=15)
        self.df: Optional[pd.DataFrame] = None
        self.X_features: Optional[csr_matrix] = None
        self.is_ready = False

    def train_and_save(self, df_full: pd.DataFrame):
        os.makedirs(self.models_dir, exist_ok=True)
        print("--- Fitting Feature Extractor ---")
        self.feature_extractor.fit(df_full)
        self.X_features = self.feature_extractor.transform(df_full)

        print("--- Fitting Auxiliary Classifiers ---")
        text_corpus = self.feature_extractor.text_vectorizer.transform(self.feature_extractor._prepare_text_corpus(df_full))
        self.difficulty_classifier.fit(text_corpus, df_full["difficulty"].values)
        self.topic_classifier.fit(text_corpus, self.feature_extractor._prepare_tags(df_full))

        print("--- Fitting Company Classifier ---")
        self.company_classifier.fit(self.X_features, df_full)

        print("--- Fitting Problem Cluster Engine ---")
        self.cluster_engine.fit(self.X_features, df_full, self.feature_extractor)

        print("--- Fitting Multi-Label Pattern Classifier ---")
        labels = np.zeros((len(df_full), 15), dtype=int)
        for i, (_, row) in enumerate(df_full.iterrows()):
            c_id = row.get("cluster_id")
            if pd.notna(c_id) and 0 <= int(c_id) < 15:
                labels[i, int(c_id)] = 1
            tag_str = " ".join(row.get("topic_tags", [])) if isinstance(row.get("topic_tags"), list) else str(row.get("topic_tags", ""))
            if "dynamic programming" in tag_str.lower(): labels[i, 13] = 1
            if "sliding window" in tag_str.lower(): labels[i, 1] = 1
            if "two pointers" in tag_str.lower(): labels[i, 0] = 1
            if "binary search" in tag_str.lower(): labels[i, 12] = 1
            if "tree" in tag_str.lower(): labels[i, 8] = 1
            if "graph" in tag_str.lower(): labels[i, 9] = 1
            if "backtracking" in tag_str.lower(): labels[i, 11] = 1
            if "greedy" in tag_str.lower(): labels[i, 14] = 1

        descriptions = df_full["problem_description"].fillna(df_full["task_id"]).tolist()
        self.pattern_classifier.fit(descriptions, labels)

        self.df = df_full.copy()
        self.df["cluster_id"] = [self.cluster_engine.kmeans.predict(self.X_features[i])[0] for i in range(len(df_full))]
        self.df["cluster_title"] = self.df["cluster_id"].map(self.cluster_engine.cluster_labels)

        # Save models
        print(f"Saving models to {self.models_dir}...")
        joblib.dump(self.feature_extractor, os.path.join(self.models_dir, "feature_extractor.joblib"))
        joblib.dump(self.difficulty_classifier, os.path.join(self.models_dir, "difficulty_classifier.joblib"))
        joblib.dump(self.topic_classifier, os.path.join(self.models_dir, "topic_classifier.joblib"))
        joblib.dump(self.company_classifier, os.path.join(self.models_dir, "company_classifier.joblib"))
        joblib.dump(self.cluster_engine, os.path.join(self.models_dir, "cluster_engine.joblib"))
        joblib.dump(self.pattern_classifier, os.path.join(self.models_dir, "pattern_classifier.joblib"))
        joblib.dump(self.X_features, os.path.join(self.models_dir, "X_features.joblib"))
        
        self.df.to_parquet(os.path.join(OUTPUT_DIR, "leetcode_with_companies_and_clusters.parquet"), index=False)
        self.is_ready = True
        print("Training complete and all models saved!")

    def load_models(self, df_full: Optional[pd.DataFrame] = None):
        print(f"Loading models from {self.models_dir}...")
        self.feature_extractor = joblib.load(os.path.join(self.models_dir, "feature_extractor.joblib"))
        
        diff_path = os.path.join(self.models_dir, "difficulty_classifier.joblib")
        if os.path.exists(diff_path):
            self.difficulty_classifier = joblib.load(diff_path)
            self.topic_classifier = joblib.load(os.path.join(self.models_dir, "topic_classifier.joblib"))
            
        self.company_classifier = joblib.load(os.path.join(self.models_dir, "company_classifier.joblib"))
        self.cluster_engine = joblib.load(os.path.join(self.models_dir, "cluster_engine.joblib"))
        self.X_features = joblib.load(os.path.join(self.models_dir, "X_features.joblib"))
        
        clustered_path = os.path.join(OUTPUT_DIR, "leetcode_with_companies_and_clusters.parquet")
        if os.path.exists(clustered_path):
            self.df = pd.read_parquet(clustered_path)
        else:
            full_path = os.path.join(OUTPUT_DIR, "leetcode_with_companies_full.parquet")
            self.df = pd.read_parquet(full_path)
            self.df["cluster_id"] = [self.cluster_engine.kmeans.predict(self.X_features[i])[0] for i in range(len(self.df))]
            self.df["cluster_title"] = self.df["cluster_id"].map(self.cluster_engine.cluster_labels)

        # Fit lightweight multi-label pattern classifier
        self.pattern_classifier = MultiLabelPatternClassifier(n_archetypes=15)
        labels = np.zeros((len(self.df), 15), dtype=int)
        for i, (_, row) in enumerate(self.df.iterrows()):
            c_id = row.get("cluster_id")
            if pd.notna(c_id) and 0 <= int(c_id) < 15:
                labels[i, int(c_id)] = 1
            tag_str = " ".join(row.get("topic_tags", [])) if isinstance(row.get("topic_tags"), list) else str(row.get("topic_tags", ""))
            if "dynamic programming" in tag_str.lower(): labels[i, 13] = 1
            if "sliding window" in tag_str.lower(): labels[i, 1] = 1
            if "two pointers" in tag_str.lower(): labels[i, 0] = 1
            if "binary search" in tag_str.lower(): labels[i, 12] = 1
            if "tree" in tag_str.lower(): labels[i, 8] = 1
            if "graph" in tag_str.lower(): labels[i, 9] = 1
            if "backtracking" in tag_str.lower(): labels[i, 11] = 1
            if "greedy" in tag_str.lower(): labels[i, 14] = 1

        descriptions = self.df["problem_description"].fillna(self.df["task_id"]).tolist()
        self.pattern_classifier.fit(descriptions, labels)

        self.is_ready = True
        print("Models successfully loaded and ready.")

    def predict_patterns(self, text: str, title: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
        """Predicts multi-label algorithmic patterns from problem text."""
        full_text = f"{title}\n{text}" if title else text
        return self.pattern_classifier.predict_patterns(full_text, threshold=0.20, top_k=top_k)

    def autoclassify_and_enrich(self, raw_problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-classifies any raw or newly scraped problem:
        - Predicts Difficulty (if missing)
        - Predicts Topic Tags (if empty)
        - Predicts Company probabilities
        - Assigns Archetype Cluster
        - Generates 5 Cross-Platform Alternatives
        - Generates 5 Similar LeetCode Counterparts
        """
        title = raw_problem.get("task_id") or raw_problem.get("title", "")
        desc = raw_problem.get("problem_description", "")
        
        # 1. Predict Difficulty if missing
        diff = raw_problem.get("difficulty")
        if not diff or diff.lower() == "none":
            text_vec = self.feature_extractor.text_vectorizer.transform([f"{title} {desc}"])
            diff, _ = self.difficulty_classifier.predict(text_vec)

        # 2. Predict Topics if empty
        tags = raw_problem.get("topic_tags")
        if not tags or len(tags) == 0:
            text_vec = self.feature_extractor.text_vectorizer.transform([f"{title} {desc}"])
            tags = self.topic_classifier.predict(text_vec)

        # 3. Vectorize multi-modal composite representation
        X_vec = self.feature_extractor.transform_single(
            title=title,
            description=desc,
            topic_tags=tags,
            difficulty=diff
        )

        # 4. Predict Cluster & Companies
        cluster_id = int(self.cluster_engine.kmeans.predict(X_vec)[0])
        cluster_title = self.cluster_engine.cluster_labels.get(cluster_id, "General Patterns")
        
        company_preds = self.company_classifier.predict_companies(X_vec, top_k=8)
        top_comps = [p["company"] for p in company_preds if p["confidence_score"] >= 45]

        # 5. Generate 5 Cross-Platform Online Judge Alternatives
        alternatives = CrossPlatformMapper.get_5_alternatives(
            task_id=raw_problem.get("task_id", ""),
            title=raw_problem.get("title"),
            topic=tags[0] if tags else None
        )

        # 6. Find 5 Top Algorithmically Similar Counterparts in DB
        similar_raw = self.cluster_engine.get_similar_problems(X_vec, top_k=5)
        similar_counterparts = []
        for idx, sim_score in similar_raw:
            p = self.df.iloc[idx]
            similar_counterparts.append({
                "question_id": int(p["question_id"]) if pd.notna(p["question_id"]) else None,
                "task_id": p["task_id"],
                "difficulty": p["difficulty"],
                "topic_tags": p["topic_tags"] if isinstance(p["topic_tags"], list) else [],
                "similarity_score": round(sim_score * 100, 1),
                "cluster_title": p.get("cluster_title", "General"),
                "leetcode_url": p.get("leetcode_url", "")
            })

        enriched = {
            "question_id": raw_problem.get("question_id") or int(abs(hash(title)) % 4000) + 3000,
            "task_id": raw_problem.get("task_id", title.lower().replace(" ", "-")),
            "title": raw_problem.get("title", title.replace("-", " ").title()),
            "difficulty": diff,
            "topic_tags": tags,
            "estimated_date": raw_problem.get("estimated_date", datetime.now().strftime("%Y-%m-%d")),
            "split": "crawled",
            "is_company_tagged": len(top_comps) > 0,
            "companies_count": len(top_comps),
            "companies": top_comps,
            "top_companies": top_comps,
            "companies_6months": top_comps[:3],
            "companies_1year": top_comps[:5],
            "companies_2year": top_comps,
            "companies_alltime": top_comps,
            "total_company_mentions": len(top_comps) * 2,
            "company_details": json.dumps({c: {"timeframes": ["alltime"], "max_frequency": 1.5} for c in top_comps}),
            "problem_description": desc,
            "starter_code": raw_problem.get("starter_code", ""),
            "completion": raw_problem.get("completion", ""),
            "entry_point": raw_problem.get("entry_point", ""),
            "test": raw_problem.get("test", ""),
            "input_output": raw_problem.get("input_output", []),
            "prompt": raw_problem.get("prompt", ""),
            "query": raw_problem.get("query", ""),
            "response": raw_problem.get("response", ""),
            "leetcode_url": f"https://leetcode.com/problems/{raw_problem.get('task_id', '')}",
            "cluster_id": cluster_id,
            "cluster_title": cluster_title,
            "predicted_companies": company_preds,
            "platform_alternatives": alternatives,
            "similar_counterparts": similar_counterparts
        }
        return enriched

    def append_and_reindex(self, enriched_problem: Dict[str, Any]):
        """Dynamically appends newly ingested problem to database and updates search index."""
        # Calculate new feature vector
        X_new = self.feature_extractor.transform_single(
            title=enriched_problem["task_id"],
            description=enriched_problem["problem_description"],
            topic_tags=enriched_problem["topic_tags"],
            difficulty=enriched_problem["difficulty"]
        )

        # Update in-memory features and dataframe
        self.X_features = vstack([self.X_features, X_new]).tocsr()
        new_row_df = pd.DataFrame([enriched_problem])
        self.df = pd.concat([self.df, new_row_df], ignore_index=True)

        # Re-index Nearest Neighbors
        self.cluster_engine.reindex(self.X_features)

        # Save to disk
        parquet_path = os.path.join(OUTPUT_DIR, "leetcode_with_companies_full.parquet")
        self.df.to_parquet(parquet_path, index=False)
        print(f"[DB] Ingested '{enriched_problem['task_id']}' -> Database now contains {len(self.df)} problems.")

    def predict_problem_companies(
        self,
        problem_description: str,
        title: str = "",
        difficulty: str = "Medium",
        topic_tags: Optional[List[str]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        if not self.is_ready:
            raise ValueError("Engine is not initialized.")

        topic_tags = topic_tags or []
        X_vec = self.feature_extractor.transform_single(
            title=title,
            description=problem_description,
            topic_tags=topic_tags,
            difficulty=difficulty
        )

        cluster_id = classify_problem_to_archetype({
            "task_id": title,
            "title": title,
            "problem_description": problem_description,
            "topic_tags": topic_tags,
            "difficulty": difficulty
        })
        cluster_info = self.cluster_engine.cluster_summaries.get(cluster_id, {})

        predictions = self.company_classifier.predict_companies(
            X_vec=X_vec,
            top_k=top_k,
            feature_extractor=self.feature_extractor,
            query_text=problem_description
        )

        # 5 Cross-Platform Alternatives
        alternatives = CrossPlatformMapper.get_5_alternatives(task_id=title, title=title, topic=topic_tags[0] if topic_tags else None)

        # 5 Closest existing LeetCode problems
        similar_raw = self.cluster_engine.get_similar_problems(X_vec, top_k=5)
        similar_problems = []
        for idx, sim_score in similar_raw:
            p = self.df.iloc[idx]
            similar_problems.append({
                "question_id": int(p["question_id"]) if pd.notna(p["question_id"]) else None,
                "task_id": p["task_id"],
                "difficulty": p["difficulty"],
                "topic_tags": p["topic_tags"] if isinstance(p["topic_tags"], list) else [],
                "companies": p["companies"] if isinstance(p["companies"], list) else [],
                "similarity_score": round(sim_score * 100, 1),
                "cluster_title": p.get("cluster_title", "General"),
                "leetcode_url": p.get("leetcode_url", "")
            })

        return {
            "predicted_companies": predictions,
            "assigned_cluster": {
                "cluster_id": cluster_id,
                "cluster_title": self.cluster_engine.cluster_labels.get(cluster_id, "General"),
                "top_tags": cluster_info.get("top_tags", []),
                "top_keywords": cluster_info.get("top_keywords", [])
            },
            "platform_alternatives": alternatives,
            "similar_existing_problems": similar_problems
        }

    def filter_and_recommend(
        self,
        company: Optional[str] = None,
        difficulty: Optional[str] = None,
        difficulty_tier: Optional[str] = None,
        topic: Optional[str] = None,
        cluster_id: Optional[int] = None,
        timeframe: Optional[str] = None,
        search_query: Optional[str] = None,
        max_direct: int = 30,
        max_similar: int = 20
    ) -> Dict[str, Any]:
        if not self.is_ready:
            raise ValueError("Engine is not initialized.")

        comp_clean = company.strip().lower() if company else None
        diff_clean = difficulty.strip().capitalize() if difficulty else None
        tier_clean = difficulty_tier.strip() if difficulty_tier else None
        topic_clean = topic.strip().lower() if topic else None
        tf_clean = timeframe.strip().lower() if timeframe else None
        q_clean = search_query.strip().lower() if search_query else None

        direct_mask = np.ones(len(self.df), dtype=bool)

        if q_clean:
            direct_mask &= self.df["task_id"].str.lower().str.contains(q_clean) | self.df["topic_tags"].apply(lambda tags: any(q_clean in str(t).lower() for t in tags) if isinstance(tags, (list, np.ndarray)) else (q_clean in str(tags).lower()))

        if comp_clean:
            if tf_clean == "6months":
                direct_mask &= self.df["companies_6months"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False)
            elif tf_clean == "1year":
                direct_mask &= self.df["companies_1year"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False)
            elif tf_clean == "2year":
                direct_mask &= self.df["companies_2year"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False)
            elif tf_clean == "alltime":
                direct_mask &= self.df["companies_alltime"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False)
            else:
                direct_mask &= self.df["companies"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False)

        if diff_clean:
            direct_mask &= (self.df["difficulty"] == diff_clean)

        if tier_clean:
            if "difficulty_tier" in self.df.columns:
                direct_mask &= (self.df["difficulty_tier"] == tier_clean)

        if cluster_id is not None and cluster_id >= 0:
            if "cluster_id" in self.df.columns:
                direct_mask &= (self.df["cluster_id"] == int(cluster_id))

        if topic_clean:
            direct_mask &= self.df["topic_tags"].apply(
                lambda tags: any(topic_clean in str(t).lower() for t in tags) if isinstance(tags, (list, np.ndarray)) else (topic_clean in str(tags).lower())
            )

        direct_indices = np.where(direct_mask)[0]
        direct_df = self.df.iloc[direct_indices].copy()

        if comp_clean:
            def get_freq(row):
                details = row.get("company_details", {})
                if isinstance(details, str):
                    try: details = json.loads(details)
                    except: details = {}
                return details.get(comp_clean, {}).get("max_frequency", 0.0) if isinstance(details, dict) else 0.0

            direct_df["query_company_frequency"] = direct_df.apply(get_freq, axis=1)
            direct_df = direct_df.sort_values(by="query_company_frequency", ascending=False)

        direct_results = []
        for _, row in direct_df.head(max_direct).iterrows():
            task_id = str(row["task_id"])
            direct_results.append({
                "question_id": int(row["question_id"]) if pd.notna(row["question_id"]) else None,
                "task_id": task_id,
                "difficulty": row["difficulty"],
                "difficulty_tier": row.get("difficulty_tier", compute_difficulty_tier(row.get("difficulty"), row.get("topic_tags"))),
                "topic_tags": row["topic_tags"] if isinstance(row["topic_tags"], list) else [],
                "companies_count": int(row.get("companies_count", 0)),
                "top_companies": row.get("top_companies", [])[:5] if isinstance(row.get("top_companies"), list) else [],
                "cluster_id": int(row.get("cluster_id", 0)),
                "cluster_title": row.get("cluster_title", "General"),
                "frequency": round(float(row.get("query_company_frequency", 0.0)), 3) if comp_clean else None,
                "leetcode_url": row.get("leetcode_url", ""),
                "platform_alternatives": CrossPlatformMapper.get_5_alternatives(task_id)
            })

        # --- Similar Unasked Problems ---
        similar_unasked_results = []
        if len(direct_indices) > 0:
            query_vector = self.X_features[direct_indices].mean(axis=0)
            query_vector = normalize(np.asarray(query_vector), norm="l2")
            query_csr = csr_matrix(query_vector)
        elif comp_clean and comp_clean in self.company_classifier.company_centroids:
            query_vector = self.company_classifier.company_centroids[comp_clean][np.newaxis, :]
            query_csr = csr_matrix(query_vector)
        else:
            query_csr = self.feature_extractor.transform_single(
                title=f"{topic_clean or ''} {comp_clean or ''}",
                description=f"Problem involving {topic_clean or 'algorithms'} with {diff_clean or 'Medium'} difficulty",
                topic_tags=[topic_clean] if topic_clean else [],
                difficulty=diff_clean or "Medium"
            )

        exclude_set = set(direct_indices)
        if comp_clean:
            comp_all_asked = np.where(self.df["companies"].apply(lambda c: comp_clean in c if isinstance(c, (list, np.ndarray)) else False))[0]
            exclude_set.update(comp_all_asked)

        candidates = self.cluster_engine.get_similar_problems(query_csr, top_k=max_similar * 2, exclude_indices=exclude_set)

        for idx, sim_score in candidates:
            row = self.df.iloc[idx]
            if diff_clean and row["difficulty"] != diff_clean:
                continue
            if topic_clean and not (any(topic_clean in str(t).lower() for t in row["topic_tags"]) if isinstance(row["topic_tags"], (list, np.ndarray)) else topic_clean in str(row["topic_tags"]).lower()):
                continue

            task_id = str(row["task_id"])
            similar_unasked_results.append({
                "question_id": int(row["question_id"]) if pd.notna(row["question_id"]) else None,
                "task_id": task_id,
                "difficulty": row["difficulty"],
                "topic_tags": row["topic_tags"] if isinstance(row["topic_tags"], list) else [],
                "similarity_score": round(sim_score * 100, 1),
                "companies_count": int(row.get("companies_count", 0)),
                "top_companies": row.get("top_companies", [])[:5] if isinstance(row.get("top_companies"), list) else [],
                "cluster_title": row.get("cluster_title", "General"),
                "reason": f"Matches {comp_clean.title() if comp_clean else 'selected'}'s interview archetype and difficulty distribution.",
                "leetcode_url": row.get("leetcode_url", ""),
                "platform_alternatives": CrossPlatformMapper.get_5_alternatives(task_id)
            })

            if len(similar_unasked_results) >= max_similar:
                break

        return {
            "query": {
                "company": comp_clean,
                "difficulty": diff_clean,
                "topic": topic_clean,
                "timeframe": tf_clean,
                "search_query": q_clean
            },
            "direct_count": len(direct_df),
            "direct_problems": direct_results,
            "similar_unasked_count": len(similar_unasked_results),
            "similar_unasked_problems": similar_unasked_results
        }

    def get_problem_by_id_or_slug(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves full details for a problem by ID or slug."""
        if self.df is None:
            return None
        
        row = None
        if identifier.isdigit():
            match = self.df[self.df["question_id"] == int(identifier)]
            if len(match) > 0: row = match.iloc[0]
        
        if row is None:
            match = self.df[self.df["task_id"] == identifier.lower()]
            if len(match) > 0: row = match.iloc[0]

        if row is None:
            return None

        task_id = str(row["task_id"])
        
        # Calculate 5 Similar Counterparts
        idx = row.name
        similar_raw = self.cluster_engine.get_similar_problems(self.X_features[idx], top_k=5, exclude_indices={idx})
        similar_counterparts = []
        for s_idx, sim_score in similar_raw:
            sp = self.df.iloc[s_idx]
            similar_counterparts.append({
                "question_id": int(sp["question_id"]) if pd.notna(sp["question_id"]) else None,
                "task_id": sp["task_id"],
                "difficulty": sp["difficulty"],
                "topic_tags": sp["topic_tags"] if isinstance(sp["topic_tags"], list) else [],
                "similarity_score": round(sim_score * 100, 1),
                "cluster_title": sp.get("cluster_title", "General"),
                "leetcode_url": sp.get("leetcode_url", "")
            })

        return {
            "question_id": int(row["question_id"]) if pd.notna(row["question_id"]) else None,
            "task_id": task_id,
            "difficulty": row["difficulty"],
            "topic_tags": row["topic_tags"] if isinstance(row["topic_tags"], list) else [],
            "estimated_date": row.get("estimated_date", ""),
            "is_company_tagged": bool(row.get("is_company_tagged", False)),
            "companies_count": int(row.get("companies_count", 0)),
            "companies": row.get("companies", []) if isinstance(row.get("companies"), list) else [],
            "top_companies": row.get("top_companies", []) if isinstance(row.get("top_companies"), list) else [],
            "companies_6months": row.get("companies_6months", []) if isinstance(row.get("companies_6months"), list) else [],
            "companies_1year": row.get("companies_1year", []) if isinstance(row.get("companies_1year"), list) else [],
            "cluster_title": row.get("cluster_title", "General"),
            "problem_description": row.get("problem_description", ""),
            "starter_code": row.get("starter_code", ""),
            "completion": row.get("completion", ""),
            "test": row.get("test", ""),
            "leetcode_url": row.get("leetcode_url", ""),
            "platform_alternatives": CrossPlatformMapper.get_5_alternatives(task_id),
            "similar_counterparts": similar_counterparts
        }


def main():
    full_dataset_path = os.path.join(OUTPUT_DIR, "leetcode_with_companies_full.parquet")
    df = pd.read_parquet(full_dataset_path)
    engine = LeetCodeIntelligenceEngine()
    engine.train_and_save(df)


if __name__ == "__main__":
    main()
