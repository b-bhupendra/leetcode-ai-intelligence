"""
Comprehensive Data Integrity & Verification Tests for Merged LeetCode Dataset
"""

import os
import json
import pandas as pd
import numpy as np

def run_tests():
    output_dir = r"C:\Users\homelap\.gemini\antigravity-ide\scratch\leetcode_dataset_merger\output"
    print("=== Running Merged Dataset Verification Tests ===")

    # 1. Test Full Parquet
    full_parquet_path = os.path.join(output_dir, "leetcode_with_companies_full.parquet")
    assert os.path.exists(full_parquet_path), "Full Parquet missing!"
    df_full = pd.read_parquet(full_parquet_path)
    assert len(df_full) >= 2869, f"Expected at least 2869 rows, got {len(df_full)}"
    assert "companies" in df_full.columns, "companies column missing!"
    assert "companies_count" in df_full.columns, "companies_count missing!"
    assert "problem_description" in df_full.columns, "problem_description missing!"
    print(f" [PASS] Full Parquet loaded: {df_full.shape} - {len(df_full)} problems verified.")

    # 2. Test Train/Test Parquet
    train_df = pd.read_parquet(os.path.join(output_dir, "leetcode_with_companies_train.parquet"))
    test_df = pd.read_parquet(os.path.join(output_dir, "leetcode_with_companies_test.parquet"))
    assert len(train_df) == 2641, f"Expected 2641 train rows, got {len(train_df)}"
    assert len(test_df) == 228, f"Expected 228 test rows, got {len(test_df)}"
    print(f" [PASS] Train ({len(train_df)}) and Test ({len(test_df)}) Parquet splits verified.")

    # 3. Test Summary CSV
    summary_csv_path = os.path.join(output_dir, "leetcode_with_companies_summary.csv")
    assert os.path.exists(summary_csv_path), "Summary CSV missing!"
    df_summary = pd.read_csv(summary_csv_path)
    assert len(df_summary) == 2869, f"Expected 2869 rows, got {len(df_summary)}"
    assert "companies" in df_summary.columns
    print(f" [PASS] Summary CSV loaded: {df_summary.shape} - 2869 rows verified.")

    # 4. Test Company Problem Matrix (CSV & Parquet)
    matrix_parquet_path = os.path.join(output_dir, "company_problem_matrix.parquet")
    matrix_csv_path = os.path.join(output_dir, "company_problem_matrix.csv")
    df_mat_pq = pd.read_parquet(matrix_parquet_path)
    df_mat_csv = pd.read_csv(matrix_csv_path)
    assert len(df_mat_pq) == len(df_mat_csv) == 20453, f"Expected 20453 rows, got {len(df_mat_pq)}"
    assert df_mat_pq["company"].nunique() == 200, f"Expected 200 companies, got {df_mat_pq['company'].nunique()}"
    print(f" [PASS] Company Problem Matrix: {len(df_mat_pq)} links across {df_mat_pq['company'].nunique()} companies.")

    # 5. Test Company Statistics Summary CSV
    stats_csv_path = os.path.join(output_dir, "company_statistics_summary.csv")
    df_stats = pd.read_csv(stats_csv_path)
    assert len(df_stats) == 200, f"Expected 200 company stats, got {len(df_stats)}"
    print(f" [PASS] Company Statistics Summary: {len(df_stats)} companies verified.")
    print("        Top 5 companies by unique problems asked:")
    for idx, row in df_stats.head(5).iterrows():
        print(f"        - {row['company']}: {row['total_unique_problems']} problems (6m: {row['problems_6months']}, 1y: {row['problems_1year']})")

    # 6. Test Excel File
    excel_path = os.path.join(output_dir, "leetcode_with_companies_report.xlsx")
    assert os.path.exists(excel_path), "Excel report missing!"
    xl = pd.ExcelFile(excel_path)
    assert "All Problems" in xl.sheet_names
    assert "Company Tagged Problems" in xl.sheet_names
    assert "Top Companies Overview" in xl.sheet_names
    print(f" [PASS] Excel Report loaded with sheets: {xl.sheet_names}")

    # 7. Test JSONL File
    jsonl_path = os.path.join(output_dir, "leetcode_with_companies_full.jsonl")
    assert os.path.exists(jsonl_path), "JSONL missing!"
    line_count = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            assert "task_id" in data
            assert "companies" in data
            line_count += 1
    assert line_count == 2869, f"Expected 2869 JSONL lines, got {line_count}"
    print(f" [PASS] JSONL file verified: {line_count} valid JSON lines.")

    # 8. Test Sample Problem Lookup: Two Sum (Question ID 1)
    two_sum = df_full[df_full["question_id"] == 1].iloc[0]
    print("\n=== Sample Enriched Problem Inspection: Two Sum (ID: 1) ===")
    print(f"Title / Task ID:        {two_sum['task_id']}")
    print(f"Difficulty:             {two_sum['difficulty']}")
    print(f"Topic Tags:             {two_sum['topic_tags']}")
    print(f"Companies Count:        {two_sum['companies_count']}")
    print(f"Top 5 Asking Companies: {two_sum['top_companies'][:5]}")
    print(f"Companies (6 months):   {two_sum['companies_6months'][:5]} ... (total {len(two_sum['companies_6months'])})")
    print(f"Companies (1 year):     {two_sum['companies_1year'][:5]} ... (total {len(two_sum['companies_1year'])})")
    print(f"Starter Code Preview:   {two_sum['starter_code'][:60]}...")
    print(f"Test Suite Length:      {len(two_sum['test'])} chars")
    
    print("\n ALL 8 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
