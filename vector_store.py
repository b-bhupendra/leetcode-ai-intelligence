"""
ChromaDB Persistent Vector Store for LeetCode Intelligence

Provides O(1) dynamic problem vector insertion, persistent HNSW indexing,
and sub-millisecond cosine similarity queries without needing full Scikit-Learn
matrix restacking or NearestNeighbors re-fitting.
"""

import os
import chromadb
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

DEFAULT_PERSIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")


class LeetCodeVectorStore:
    def __init__(self, persist_directory: str = DEFAULT_PERSIST_DIR):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Get or create collection with HNSW cosine metric space
        self.collection = self.client.get_or_create_collection(
            name="leetcode_problems",
            metadata={"hnsw:space": "cosine"}
        )

    def count(self) -> int:
        """Returns the total number of indexed vectors."""
        return self.collection.count()

    def batch_ingest_from_dataframe(self, df: pd.DataFrame, feature_matrix: np.ndarray):
        """
        Batch seeds the ChromaDB collection with dense feature representations
        and comprehensive metadata.
        """
        if self.count() >= len(df):
            print(f"[VectorStore] Collection already indexed with {self.count()} vectors. Skipping seed.")
            return

        print(f"[VectorStore] Seeding {len(df)} problems into persistent ChromaDB...")
        
        # Convert sparse to dense if needed
        if hasattr(feature_matrix, "toarray"):
            dense_vectors = feature_matrix.toarray().tolist()
        else:
            dense_vectors = feature_matrix.tolist()

        ids = [str(r.get("question_id", idx)) for idx, r in df.iterrows()]
        
        metadatas = []
        documents = []
        
        for _, r in df.iterrows():
            task_id = str(r.get("task_id", ""))
            title = str(r.get("title", task_id))
            diff = str(r.get("difficulty", "Medium"))
            cluster_id = int(r.get("cluster_id", 0)) if pd.notna(r.get("cluster_id")) else 0
            cluster_title = str(r.get("cluster_title", "General Algorithm"))
            comp_count = int(r.get("companies_count", 0)) if pd.notna(r.get("companies_count")) else 0
            
            topics = r.get("topic_tags", [])
            topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)
            
            metadatas.append({
                "task_id": task_id,
                "title": title,
                "difficulty": diff,
                "cluster_id": cluster_id,
                "cluster_title": cluster_title,
                "companies_count": comp_count,
                "topics": topics_str[:300]
            })
            documents.append(f"{title} | {diff} | {cluster_title} | {topics_str}")

        # Batch insert in chunks of 500
        chunk_size = 500
        for i in range(0, len(ids), chunk_size):
            end = min(i + chunk_size, len(ids))
            self.collection.upsert(
                ids=ids[i:end],
                embeddings=dense_vectors[i:end],
                metadatas=metadatas[i:end],
                documents=documents[i:end]
            )
            
        print(f"[VectorStore] Successfully indexed {self.collection.count()} vectors in ChromaDB.")

    def append_problem(self, enriched_problem: Dict[str, Any], vector: np.ndarray):
        """
        O(1) Dynamic Vector Insertion without rebuilding the index.
        """
        qid = str(enriched_problem.get("question_id", enriched_problem.get("task_id", "unknown")))
        
        if hasattr(vector, "toarray"):
            dense_vec = vector.toarray().flatten().tolist()
        elif hasattr(vector, "flatten"):
            dense_vec = vector.flatten().tolist()
        else:
            dense_vec = list(vector)

        task_id = str(enriched_problem.get("task_id", ""))
        title = str(enriched_problem.get("title", task_id))
        diff = str(enriched_problem.get("difficulty", "Medium"))
        cluster_id = int(enriched_problem.get("cluster_id", 0))
        cluster_title = str(enriched_problem.get("cluster_title", "Dynamic Ingested Archetype"))
        comp_count = int(enriched_problem.get("companies_count", 0))
        topics = enriched_problem.get("topic_tags", [])
        topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)

        metadata = {
            "task_id": task_id,
            "title": title,
            "difficulty": diff,
            "cluster_id": cluster_id,
            "cluster_title": cluster_title,
            "companies_count": comp_count,
            "topics": topics_str[:300]
        }

        self.collection.upsert(
            ids=[qid],
            embeddings=[dense_vec],
            metadatas=[metadata],
            documents=[f"{title} | {diff} | {cluster_title} | {topics_str}"]
        )

    def get_similar_problems(self, query_vector: np.ndarray, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Sub-millisecond HNSW cosine similarity search.
        """
        if hasattr(query_vector, "toarray"):
            dense_vec = query_vector.toarray().flatten().tolist()
        elif hasattr(query_vector, "flatten"):
            dense_vec = query_vector.flatten().tolist()
        else:
            dense_vec = list(query_vector)

        kwargs = {
            "query_embeddings": [dense_vec],
            "n_results": min(top_k, max(1, self.collection.count()))
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)
        
        similar_items = []
        if results and "ids" in results and len(results["ids"]) > 0:
            for idx in range(len(results["ids"][0])):
                qid = results["ids"][0][idx]
                dist = results["distances"][0][idx] if "distances" in results and results["distances"] else 0.0
                meta = results["metadatas"][0][idx] if "metadatas" in results and results["metadatas"] else {}
                
                # Cosine distance to similarity percentage
                sim_score = max(0.0, min(100.0, round((1.0 - dist) * 100.0, 1)))
                
                similar_items.append({
                    "question_id": qid,
                    "task_id": meta.get("task_id", ""),
                    "title": meta.get("title", ""),
                    "difficulty": meta.get("difficulty", ""),
                    "cluster_id": meta.get("cluster_id", 0),
                    "cluster_title": meta.get("cluster_title", ""),
                    "similarity_score": sim_score
                })
                
        return similar_items
