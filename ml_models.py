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


class ProblemClusterEngine:
    """
    Unsupervised problem clustering into algorithmic archetypes + NearestNeighbors similarity index.
    """
    def __init__(self, n_clusters: int = 30):
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            random_state=42,
            batch_size=256,
            n_init=10
        )
        self.nn_index = NearestNeighbors(metric="cosine", algorithm="brute")
        self.cluster_labels: Dict[int, str] = {}
        self.cluster_summaries: Dict[int, Dict[str, Any]] = {}
        self.is_fitted = False

    def fit(self, X: csr_matrix, df: pd.DataFrame, feature_extractor: LeetCodeFeatureExtractor):
        print(f"Clustering {X.shape[0]} LeetCode problems into {self.n_clusters} algorithmic archetypes...")
        cluster_ids = self.kmeans.fit_predict(X)
        self.nn_index.fit(X)

        df["cluster_id"] = cluster_ids
        terms = np.array(feature_extractor.text_vectorizer.get_feature_names_out())
        
        seen_titles = set()
        for c_id in range(self.n_clusters):
            c_members = df[df["cluster_id"] == c_id]
            size = len(c_members)
            
            # 1. Extract Top Topic Tags
            all_tags = []
            for tags in c_members["topic_tags"]:
                if isinstance(tags, (list, np.ndarray)):
                    all_tags.extend(tags)
                elif isinstance(tags, str) and tags.strip():
                    all_tags.extend([t.strip() for t in tags.split(";")])
            
            tag_counts = pd.Series(all_tags).value_counts()
            top_tags = tag_counts.head(4).index.tolist() if not tag_counts.empty else ["Algorithms"]
            
            # 2. Extract Top Distinctive TF-IDF Keywords from Cluster Centroid
            center = self.kmeans.cluster_centers_[c_id][:len(terms)]
            top_word_indices = center.argsort()[::-1][:5]
            top_words = [terms[i] for i in top_word_indices if i < len(terms)]
            
            # 3. Determine Dominant Difficulty
            diff_dist = c_members["difficulty"].value_counts().to_dict()
            dominant_diff = max(diff_dist, key=diff_dist.get) if diff_dist else "Medium"

            # 4. Generate Unique Disambiguated Title
            primary_tag = top_tags[0] if top_tags else "General"
            sec_tag = top_tags[1] if len(top_tags) > 1 else "Patterns"
            keyword_sub = top_words[0].title() if top_words else "Optimization"
            
            cluster_title = f"{dominant_diff} {primary_tag} & {sec_tag} ({keyword_sub})"
            if cluster_title in seen_titles:
                # If collision occurs, use second keyword or cluster ID disambiguation
                keyword_alt = top_words[1].title() if len(top_words) > 1 else f"Type {c_id}"
                cluster_title = f"{dominant_diff} {primary_tag} & {sec_tag} ({keyword_alt})"
            seen_titles.add(cluster_title)
            
            self.cluster_labels[c_id] = cluster_title
            sample_titles = c_members["task_id"].head(5).tolist()

            self.cluster_summaries[c_id] = {
                "cluster_id": c_id,
                "title": cluster_title,
                "size": size,
                "problem_count": size,
                "description": f"{dominant_diff}-level interview pattern focusing on {primary_tag}, {sec_tag}, and {', '.join(top_words[:3])} structures.",
                "top_tags": top_tags,
                "top_keywords": top_words,
                "difficulty_distribution": diff_dist,
                "sample_problems": sample_titles
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

        self.is_ready = True
        print("Models successfully loaded and ready.")

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

        cluster_id = int(self.cluster_engine.kmeans.predict(X_vec)[0])
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
        topic: Optional[str] = None,
        timeframe: Optional[str] = None,
        search_query: Optional[str] = None,
        max_direct: int = 30,
        max_similar: int = 20
    ) -> Dict[str, Any]:
        if not self.is_ready:
            raise ValueError("Engine is not initialized.")

        comp_clean = company.strip().lower() if company else None
        diff_clean = difficulty.strip().capitalize() if difficulty else None
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
                "topic_tags": row["topic_tags"] if isinstance(row["topic_tags"], list) else [],
                "companies_count": int(row.get("companies_count", 0)),
                "top_companies": row.get("top_companies", [])[:5] if isinstance(row.get("top_companies"), list) else [],
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
