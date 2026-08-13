"""
LeetCode Company-Enriched Dataset Loader for Pandas

Provides easy-to-use functions to load, filter, and inspect the merged LeetCode datasets.
"""

import os
import pandas as pd
from typing import List, Optional, Union

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

def load_full_dataset(
    output_dir: str = DEFAULT_OUTPUT_DIR,
    split: Optional[str] = None
) -> pd.DataFrame:
    """
    Loads the full LeetCode dataset with all code, test cases, reasoning responses,
    and structured company tags.

    Args:
        output_dir: Path to output directory containing parquet files.
        split: Optional filter for 'train' or 'test'. If None, loads all 2,869 problems.

    Returns:
        pd.DataFrame containing the rich dataset.
    """
    if split == "train":
        path = os.path.join(output_dir, "leetcode_with_companies_train.parquet")
    elif split == "test":
        path = os.path.join(output_dir, "leetcode_with_companies_test.parquet")
    else:
        path = os.path.join(output_dir, "leetcode_with_companies_full.parquet")

    return pd.read_parquet(path)


def load_summary_dataset(output_dir: str = DEFAULT_OUTPUT_DIR) -> pd.DataFrame:
    """
    Loads the tabular metadata summary CSV (without heavy code/test strings).
    Perfect for fast table analysis and Excel-like exploration.
    """
    path = os.path.join(output_dir, "leetcode_with_companies_summary.csv")
    return pd.read_csv(path)


def load_company_problem_matrix(
    output_dir: str = DEFAULT_OUTPUT_DIR,
    use_parquet: bool = True
) -> pd.DataFrame:
    """
    Loads the flattened relational table mapping each company + timeframe to problem details.
    
    Columns:
        ['company', 'timeframe', 'question_id', 'task_id', 'title',
         'difficulty', 'frequency', 'acceptance', 'in_hf_dataset', 'leetcode_url']
    """
    if use_parquet:
        path = os.path.join(output_dir, "company_problem_matrix.parquet")
        return pd.read_parquet(path)
    else:
        path = os.path.join(output_dir, "company_problem_matrix.csv")
        return pd.read_csv(path)


def get_problems_by_company(
    company_name: str,
    timeframe: Optional[str] = None,
    difficulty: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR
) -> pd.DataFrame:
    """
    Filters and returns problems asked by a specific company.

    Args:
        company_name: Name of the company (e.g. 'google', 'amazon', 'meta', 'apple').
        timeframe: Optional timeframe filter ('6months', '1year', '2year', 'alltime').
        difficulty: Optional difficulty filter ('Easy', 'Medium', 'Hard').
    """
    df = load_company_problem_matrix(output_dir)
    comp_lower = company_name.strip().lower()
    filtered = df[df["company"] == comp_lower]

    if timeframe:
        filtered = filtered[filtered["timeframe"] == timeframe.lower()]
    if difficulty:
        filtered = filtered[filtered["difficulty"].str.lower() == difficulty.lower()]

    return filtered.sort_values(by="frequency", ascending=False)


def search_problems_by_company_tag(
    df: pd.DataFrame,
    company_name: str,
    timeframe: Optional[str] = None
) -> pd.DataFrame:
    """
    Searches the full enriched DataFrame for problems containing the given company tag.
    
    Args:
        df: Enriched DataFrame from load_full_dataset().
        company_name: Name of company to search for.
        timeframe: '6months', '1year', '2year', 'alltime', or None for any.
    """
    comp_lower = company_name.strip().lower()
    
    if timeframe == "6months":
        mask = df["companies_6months"].apply(lambda comps: comp_lower in comps if isinstance(comps, (list, np.ndarray)) else False)
    elif timeframe == "1year":
        mask = df["companies_1year"].apply(lambda comps: comp_lower in comps if isinstance(comps, (list, np.ndarray)) else False)
    elif timeframe == "2year":
        mask = df["companies_2year"].apply(lambda comps: comp_lower in comps if isinstance(comps, (list, np.ndarray)) else False)
    elif timeframe == "alltime":
        mask = df["companies_alltime"].apply(lambda comps: comp_lower in comps if isinstance(comps, (list, np.ndarray)) else False)
    else:
        mask = df["companies"].apply(lambda comps: comp_lower in comps if isinstance(comps, (list, np.ndarray)) else False)

    return df[mask]


if __name__ == "__main__":
    print("Testing loader functions...")
    
    # 1. Test Summary Loader
    summary_df = load_summary_dataset()
    print(f"Summary dataset loaded: {summary_df.shape[0]} rows, {summary_df.shape[1]} columns")

    # 2. Test Full Dataset Loader
    full_df = load_full_dataset()
    print(f"Full dataset loaded: {full_df.shape[0]} rows, {full_df.shape[1]} columns")

    # 3. Test Company Problem Matrix Loader
    matrix_df = load_company_problem_matrix()
    print(f"Company matrix loaded: {matrix_df.shape[0]} rows across {matrix_df['company'].nunique()} companies")

    # 4. Test Filtering by Company
    google_problems = get_problems_by_company("google", timeframe="6months")
    print(f"Google 6-months problems count: {len(google_problems)}")
    print(google_problems[["question_id", "title", "difficulty", "frequency"]].head())
