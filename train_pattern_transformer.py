"""
CodeBERT / Transformer Multi-Label Fine-Tuning Pipeline for DSA Pattern Classification

Frames LeetCode problem description understanding as an NLP Multi-Label Text Classification task
mapping text embeddings to the 15 Unified Algorithmic Archetypes using Binary Cross-Entropy Loss.
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
import torch
from typing import Dict, Any, List

try:
    from datasets import Dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer,
        EvalPrediction
    )
    from sklearn.metrics import f1_score, roc_auc_score, accuracy_score
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from ml_models import ARCHETYPES_TAXONOMY, clean_problem_text_for_nlp

MODEL_NAME = "microsoft/codebert-base"
NUM_ARCHETYPES = 15


def load_problem_dataset(parquet_path: str = "output/leetcode_with_companies_and_clusters.parquet"):
    if not os.path.exists(parquet_path):
        parquet_path = "output/leetcode_with_companies_full.parquet"
    
    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df)} problems from {parquet_path}")

    # Build multi-hot label matrix
    multi_hot_labels = []
    descriptions = []

    for _, row in df.iterrows():
        label_vec = [0.0] * NUM_ARCHETYPES
        c_id = row.get("cluster_id")
        if pd.notna(c_id) and 0 <= int(c_id) < NUM_ARCHETYPES:
            label_vec[int(c_id)] = 1.0

        tag_str = " ".join(row.get("topic_tags", [])) if isinstance(row.get("topic_tags"), list) else str(row.get("topic_tags", ""))
        if "dynamic programming" in tag_str.lower(): label_vec[13] = 1.0
        if "sliding window" in tag_str.lower(): label_vec[1] = 1.0
        if "two pointers" in tag_str.lower(): label_vec[0] = 1.0
        if "binary search" in tag_str.lower(): label_vec[12] = 1.0
        if "tree" in tag_str.lower(): label_vec[8] = 1.0
        if "graph" in tag_str.lower(): label_vec[9] = 1.0
        if "backtracking" in tag_str.lower(): label_vec[11] = 1.0
        if "greedy" in tag_str.lower(): label_vec[14] = 1.0

        raw_desc = str(row.get("problem_description", "")) or str(row.get("task_id", ""))
        cleaned = clean_problem_text_for_nlp(raw_desc)
        
        descriptions.append(cleaned)
        multi_hot_labels.append(label_vec)

    return pd.DataFrame({"description": descriptions, "labels": multi_hot_labels})


def compute_metrics(p: "EvalPrediction"):
    preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
    probs = 1 / (1 + np.exp(-preds))
    y_pred = np.where(probs >= 0.5, 1, 0)
    y_true = p.label_ids
    return {
        'f1_micro': float(f1_score(y_true, y_pred, average='micro', zero_division=0)),
        'f1_macro': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
        'accuracy': float(accuracy_score(y_true, y_pred))
    }


def train_codebert_classifier(output_dir: str = "./leetcode-pattern-codebert", epochs: int = 4, batch_size: int = 8):
    if not HAS_TRANSFORMERS:
        print("[ERROR] 'transformers' and 'datasets' packages are required for CodeBERT training.")
        print("Run: pip install transformers datasets torch accelerate")
        return

    print(f"--- Fine-Tuning CodeBERT on 15 Algorithmic Archetypes ---")
    df = load_problem_dataset()
    dataset = Dataset.from_pandas(df)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def preprocess_function(examples):
        batch = tokenizer(
            examples["description"],
            padding="max_length",
            truncation=True,
            max_length=512
        )
        batch["labels"] = [[float(l) for l in label] for label in examples["labels"]]
        return batch

    encoded_dataset = dataset.map(preprocess_function, batched=True)
    split_dataset = encoded_dataset.train_test_split(test_size=0.15, seed=42)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_ARCHETYPES,
        problem_type="multi_label_classification"
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        logging_steps=50
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    print("Starting PyTorch training loop...")
    trainer.train()
    print(f"[SUCCESS] Model saved to {output_dir}")


def predict_pattern_standalone(text: str, model_dir: str = "./leetcode-pattern-codebert", threshold: float = 0.3):
    if not HAS_TRANSFORMERS or not os.path.exists(model_dir):
        print(f"Transformer model not found at {model_dir}. Using Scikit-Learn MultiLabelPatternClassifier fallback.")
        from ml_models import LeetCodeIntelligenceEngine
        engine = LeetCodeIntelligenceEngine()
        engine.load_models()
        return engine.predict_patterns(text)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]

    results = []
    for i in range(NUM_ARCHETYPES):
        arch = ARCHETYPES_TAXONOMY[i]
        results.append({
            "archetype_id": i,
            "name": arch["name"],
            "paradigm": arch["paradigm"],
            "probability": round(float(probs[i]), 4),
            "confidence_pct": round(float(probs[i]) * 100, 1),
            "invariant": arch["invariant"],
            "gfg_topic": arch["gfg_topic"],
            "gfg_url": arch["gfg_url"]
        })
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodeBERT Multi-Label DSA Pattern Classifier")
    parser.add_argument("--train", action="store_true", help="Train the CodeBERT model")
    parser.add_argument("--epochs", type=int, default=4, help="Number of training epochs")
    parser.add_argument("--text", type=str, help="Problem text to classify")
    args = parser.parse_args()

    if args.train:
        train_codebert_classifier(epochs=args.epochs)
    elif args.text:
        preds = predict_pattern_standalone(args.text)
        print(json.dumps(preds, indent=2))
    else:
        print("Usage:")
        print("  Train:   python train_pattern_transformer.py --train --epochs 4")
        print("  Predict: python train_pattern_transformer.py --text 'Given an array of integers nums and target, find subarray sum'")
