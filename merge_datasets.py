import os
import glob
import re
import json
from collections import defaultdict
import pandas as pd
import numpy as np
from tqdm import tqdm

def clean_str(val):
    if val is None or pd.isna(val):
        return ""
    return str(val).strip()

def parse_company_data(raw_company_dir):
    """
    Parses all 537 CSV files in the raw company data directory.
    Returns:
      - company_by_qid: mapping from question_id (int) -> dict of company info
      - company_by_slug: mapping from slug (str) -> question_id (int)
      - flat_records: list of flattened (company, timeframe, qid, slug, title, diff, freq, acc)
      - all_companies: set of all unique company names
    """
    csv_files = glob.glob(os.path.join(raw_company_dir, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in {raw_company_dir}")

    company_by_qid = defaultdict(lambda: {
        "companies": set(),
        "timeframe_companies": {"6months": set(), "1year": set(), "2year": set(), "alltime": set()},
        "company_details": {},  # comp -> {"timeframes": [], "frequencies": {}, "max_frequency": 0.0, "acceptance": ""}
        "titles": set(),
        "slugs": set(),
        "difficulties": set(),
        "acceptance_rates": set(),
        "links": set()
    })
    
    company_by_slug = {}
    flat_records = []
    all_companies = set()

    for fpath in tqdm(csv_files, desc="Parsing Company CSVs"):
        fname = os.path.basename(fpath)
        m = re.match(r"^(.*)_(alltime|6months|1year|2year)\.csv$", fname, re.IGNORECASE)
        if not m:
            continue
        
        company = m.group(1).lower()
        timeframe = m.group(2).lower()
        all_companies.add(company)

        try:
            df = pd.read_csv(fpath)
            df.columns = [c.strip() for c in df.columns]
            
            for _, row in df.iterrows():
                raw_id = clean_str(row.get("ID", ""))
                if not raw_id or raw_id.lower() == "nan":
                    continue
                try:
                    qid = int(float(raw_id))
                except ValueError:
                    continue

                title = clean_str(row.get("Title", ""))
                link = clean_str(row.get("Leetcode Question Link", ""))
                slug = link.rstrip("/").split("/")[-1] if "leetcode.com/problems/" in link else ""
                diff = clean_str(row.get("Difficulty", ""))
                acc = clean_str(row.get("Acceptance", ""))
                
                try:
                    freq = float(clean_str(row.get("Frequency", "0")))
                except ValueError:
                    freq = 0.0

                entry = company_by_qid[qid]
                entry["companies"].add(company)
                entry["timeframe_companies"][timeframe].add(company)
                
                if company not in entry["company_details"]:
                    entry["company_details"][company] = {
                        "timeframes": [],
                        "frequencies": {},
                        "max_frequency": 0.0,
                        "acceptance": acc
                    }
                
                comp_stat = entry["company_details"][company]
                if timeframe not in comp_stat["timeframes"]:
                    comp_stat["timeframes"].append(timeframe)
                comp_stat["frequencies"][timeframe] = freq
                comp_stat["max_frequency"] = max(comp_stat["max_frequency"], freq)
                if acc and not comp_stat["acceptance"]:
                    comp_stat["acceptance"] = acc

                if title:
                    entry["titles"].add(title)
                if slug:
                    entry["slugs"].add(slug)
                    company_by_slug[slug] = qid
                if diff:
                    entry["difficulties"].add(diff)
                if acc:
                    entry["acceptance_rates"].add(acc)
                if link:
                    entry["links"].add(link)

                flat_records.append({
                    "company": company,
                    "timeframe": timeframe,
                    "question_id": qid,
                    "task_id": slug,
                    "title": title,
                    "difficulty": diff,
                    "frequency": freq,
                    "acceptance": acc,
                    "leetcode_url": link
                })

        except Exception as e:
            print(f"Error parsing {fname}: {e}")

    print(f"Processed {len(company_by_qid)} unique problems asked across {len(all_companies)} companies.")
    return company_by_qid, company_by_slug, flat_records, all_companies


def load_hf_dataset(raw_hf_dir):
    """
    Loads train and test splits of the Hugging Face LeetCodeDataset.
    """
    train_path = os.path.join(raw_hf_dir, "LeetCodeDataset-train.jsonl")
    test_path = os.path.join(raw_hf_dir, "LeetCodeDataset-test.jsonl")

    records = []
    
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            item = json.loads(line)
            item["split"] = "train"
            records.append(item)

    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            item = json.loads(line)
            item["split"] = "test"
            records.append(item)

    print(f"Loaded {len(records)} problems from Hugging Face dataset (Train: {sum(1 for r in records if r['split']=='train')}, Test: {sum(1 for r in records if r['split']=='test')})")
    return records


def merge_and_enrich(hf_records, company_by_qid, company_by_slug):
    """
    Merges HF problems with company tags.
    """
    enriched_problems = []
    seen_qids = set()

    for item in hf_records:
        raw_qid = item.get("question_id")
        try:
            qid = int(raw_qid)
        except (ValueError, TypeError):
            qid = None

        slug = item.get("task_id", "")
        if qid is not None:
            seen_qids.add(qid)

        # Lookup company information
        comp_info = None
        if qid in company_by_qid:
            comp_info = company_by_qid[qid]
        elif slug in company_by_slug:
            comp_info = company_by_qid[company_by_slug[slug]]

        if comp_info:
            all_comps = sorted(list(comp_info["companies"]))
            # Sort top companies by their highest frequency score
            top_comps = sorted(
                all_comps,
                key=lambda c: comp_info["company_details"].get(c, {}).get("max_frequency", 0.0),
                reverse=True
            )
            comps_6m = sorted(list(comp_info["timeframe_companies"]["6months"]))
            comps_1y = sorted(list(comp_info["timeframe_companies"]["1year"]))
            comps_2y = sorted(list(comp_info["timeframe_companies"]["2year"]))
            comps_alltime = sorted(list(comp_info["timeframe_companies"]["alltime"]))
            details = comp_info["company_details"]
            total_mentions = sum(len(d["timeframes"]) for d in details.values())
            is_tagged = True
        else:
            all_comps = []
            top_comps = []
            comps_6m = []
            comps_1y = []
            comps_2y = []
            comps_alltime = []
            details = {}
            total_mentions = 0
            is_tagged = False

        # Topic tags from HF (list of strings)
        topic_tags = item.get("tags", [])
        if isinstance(topic_tags, str):
            try:
                topic_tags = json.loads(topic_tags)
            except Exception:
                topic_tags = [topic_tags] if topic_tags else []

        enriched = {
            # Problem Identifiers & Core Metadata
            "question_id": qid,
            "task_id": slug,
            "difficulty": item.get("difficulty", ""),
            "topic_tags": topic_tags,
            "estimated_date": item.get("estimated_date", ""),
            "split": item.get("split", ""),
            
            # Enriched Company Tags
            "is_company_tagged": is_tagged,
            "companies_count": len(all_comps),
            "companies": all_comps,
            "top_companies": top_comps,
            "companies_6months": comps_6m,
            "companies_1year": comps_1y,
            "companies_2year": comps_2y,
            "companies_alltime": comps_alltime,
            "total_company_mentions": total_mentions,
            "company_details": json.dumps(details, ensure_ascii=False),
            
            # Content & Code
            "problem_description": item.get("problem_description", ""),
            "starter_code": item.get("starter_code", ""),
            "completion": item.get("completion", ""),
            "entry_point": item.get("entry_point", ""),
            "test": item.get("test", ""),
            "input_output": item.get("input_output", []),
            "prompt": item.get("prompt", ""),
            "query": item.get("query", ""),
            "response": item.get("response", ""),
            "leetcode_url": f"https://leetcode.com/problems/{slug}" if slug else ""
        }
        enriched_problems.append(enriched)

    return enriched_problems


def generate_outputs(enriched_problems, flat_records, all_companies, output_dir):
    """
    Writes out all formatted files into output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nGenerating datasets in: {output_dir}")

    # 1. Full Dataset in Parquet (native list/dict support, fast loading)
    df_full = pd.DataFrame(enriched_problems)
    parquet_full_path = os.path.join(output_dir, "leetcode_with_companies_full.parquet")
    df_full.to_parquet(parquet_full_path, index=False, engine="pyarrow")
    print(f" -> Generated Full Parquet: {parquet_full_path} ({os.path.getsize(parquet_full_path)/(1024*1024):.2f} MB)")

    # 1b. Train and Test Split Parquet files
    df_train = df_full[df_full["split"] == "train"]
    df_test = df_full[df_full["split"] == "test"]
    train_parquet_path = os.path.join(output_dir, "leetcode_with_companies_train.parquet")
    test_parquet_path = os.path.join(output_dir, "leetcode_with_companies_test.parquet")
    df_train.to_parquet(train_parquet_path, index=False, engine="pyarrow")
    df_test.to_parquet(test_parquet_path, index=False, engine="pyarrow")
    print(f" -> Generated Train Parquet: {train_parquet_path}")
    print(f" -> Generated Test Parquet:  {test_parquet_path}")

    # 2. Full Dataset in JSONL (compatible with all LLM tools and json lines reader)
    jsonl_full_path = os.path.join(output_dir, "leetcode_with_companies_full.jsonl")
    with open(jsonl_full_path, "w", encoding="utf-8") as f:
        for p in enriched_problems:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f" -> Generated Full JSONL: {jsonl_full_path} ({os.path.getsize(jsonl_full_path)/(1024*1024):.2f} MB)")

    # 3. Tabular Summary CSV (Easy for Excel and fast pd.read_csv without 10KB code strings)
    summary_cols = [
        "question_id", "task_id", "difficulty", "topic_tags", "estimated_date", "split",
        "is_company_tagged", "companies_count", "companies", "top_companies",
        "companies_6months", "companies_1year", "companies_2year", "companies_alltime",
        "total_company_mentions", "leetcode_url"
    ]
    df_summary = df_full[summary_cols].copy()
    
    # Format list fields as clean semicolon-delimited strings for CSV/Excel compatibility
    for col in ["topic_tags", "companies", "top_companies", "companies_6months", "companies_1year", "companies_2year", "companies_alltime"]:
        df_summary[col] = df_summary[col].apply(lambda x: "; ".join(x) if isinstance(x, (list, set)) else clean_str(x))

    summary_csv_path = os.path.join(output_dir, "leetcode_with_companies_summary.csv")
    df_summary.to_csv(summary_csv_path, index=False, encoding="utf-8")
    print(f" -> Generated Summary CSV: {summary_csv_path} ({os.path.getsize(summary_csv_path)/(1024*1024):.2f} MB)")

    # 4. Flat Relational Company-Problem Matrix (CSV and Parquet)
    df_flat = pd.DataFrame(flat_records)
    # Add whether problem is in HF dataset
    hf_qids = set(df_full["question_id"].dropna().astype(int))
    df_flat["in_hf_dataset"] = df_flat["question_id"].isin(hf_qids)

    flat_csv_path = os.path.join(output_dir, "company_problem_matrix.csv")
    flat_parquet_path = os.path.join(output_dir, "company_problem_matrix.parquet")
    df_flat.to_csv(flat_csv_path, index=False, encoding="utf-8")
    df_flat.to_parquet(flat_parquet_path, index=False, engine="pyarrow")
    print(f" -> Generated Company-Problem Matrix CSV: {flat_csv_path}")
    print(f" -> Generated Company-Problem Matrix Parquet: {flat_parquet_path}")

    # 5. Company Overview Aggregation
    company_stats = []
    for comp in sorted(list(all_companies)):
        comp_df = df_flat[df_flat["company"] == comp]
        unique_probs = comp_df["question_id"].nunique()
        tf_counts = comp_df.groupby("timeframe")["question_id"].nunique().to_dict()
        diff_counts = comp_df.groupby("difficulty")["question_id"].nunique().to_dict()
        company_stats.append({
            "company": comp,
            "total_unique_problems": unique_probs,
            "problems_6months": tf_counts.get("6months", 0),
            "problems_1year": tf_counts.get("1year", 0),
            "problems_2year": tf_counts.get("2year", 0),
            "problems_alltime": tf_counts.get("alltime", 0),
            "easy_count": diff_counts.get("Easy", 0),
            "medium_count": diff_counts.get("Medium", 0),
            "hard_count": diff_counts.get("Hard", 0),
        })
    df_comp_stats = pd.DataFrame(company_stats).sort_values("total_unique_problems", ascending=False)
    comp_stats_csv_path = os.path.join(output_dir, "company_statistics_summary.csv")
    df_comp_stats.to_csv(comp_stats_csv_path, index=False, encoding="utf-8")
    print(f" -> Generated Company Stats CSV: {comp_stats_csv_path}")

    # 6. Multi-Sheet Excel Report
    excel_path = os.path.join(output_dir, "leetcode_with_companies_report.xlsx")
    print(f"Writing Excel report to {excel_path} (this may take a few seconds)...")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="All Problems", index=False)
        df_summary[df_summary["is_company_tagged"]].to_excel(writer, sheet_name="Company Tagged Problems", index=False)
        df_comp_stats.to_excel(writer, sheet_name="Top Companies Overview", index=False)
        df_flat.head(10000).to_excel(writer, sheet_name="Company-Problem Sample", index=False)
    print(f" -> Generated Excel Report: {excel_path} ({os.path.getsize(excel_path)/(1024*1024):.2f} MB)")

    print("\n=== Dataset Merge Complete ===")
    print(f"Total Hugging Face Problems: {len(df_full)}")
    print(f"Problems with Company Tags:   {df_full['is_company_tagged'].sum()} ({df_full['is_company_tagged'].mean()*100:.1f}%)")
    print(f"Distinct Companies Tagged:   {len(all_companies)}")
    print(f"Total (Company, Problem) Links: {len(df_flat)}")


def main():
    base_dir = r"C:\Users\homelap\.gemini\antigravity-ide\scratch\leetcode_dataset_merger"
    raw_company_dir = os.path.join(base_dir, "raw_company_data")
    raw_hf_dir = os.path.join(base_dir, "raw_hf_data")
    output_dir = os.path.join(base_dir, "output")

    company_by_qid, company_by_slug, flat_records, all_companies = parse_company_data(raw_company_dir)
    hf_records = load_hf_dataset(raw_hf_dir)
    enriched_problems = merge_and_enrich(hf_records, company_by_qid, company_by_slug)
    generate_outputs(enriched_problems, flat_records, all_companies, output_dir)


if __name__ == "__main__":
    main()
