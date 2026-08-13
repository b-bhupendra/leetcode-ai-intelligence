"""
Export AI-Readable Codebase Digest

Creates a single, clean markdown document (AI_READABLE_CODEBASE.md)
containing the full source code and architecture with 0 binary artifacts,
making it 100% readable by any LLM (ChatGPT, Claude, DeepSeek, Gemini).
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIGEST_FILE = os.path.join(ROOT_DIR, "AI_READABLE_CODEBASE.md")

FILES_TO_INCLUDE = [
    "README.md",
    "requirements.txt",
    "queue_manager.py",
    "vector_store.py",
    "mcp_server.py",
    "web_app.py",
    "ml_models.py",
    "scraper_engine.py",
    "agent_queue_worker.py",
    "load_data.py",
    "merge_datasets.py",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/src/App.jsx",
    "frontend/src/components/LayoutWrapper.jsx",
    "frontend/src/components/ProblemCard.jsx",
    "frontend/src/components/ProblemExplorer.jsx",
    "frontend/src/components/LiveCopilotStream.jsx",
    "frontend/src/components/ProblemInspectorDrawer.jsx",
    "frontend/src/components/AICompanyPredictor.jsx",
    "frontend/src/components/ArchetypeClusters.jsx",
    "frontend/src/components/CrawlerConsole.jsx",
    "test_sqlite_queue_and_vector_store.py",
    "test_mcp_bridge.py",
    "test_query_queue_and_worker.py",
    "test_scraper_and_autoclassifier.py",
    "test_ml_pipeline.py",
    "test_merged_data.py",
    "test_web_api.py"
]


def generate_digest():
    print("Generating AI-Readable Codebase Digest...")
    lines = []
    lines.append("# 🧠 LeetCode AI Intelligence - Full Plain-Text Codebase Digest\n")
    lines.append("> This single document contains the complete plain-text source code and architecture of the platform, optimized for ingestion by Large Language Models.\n\n")

    lines.append("## 📁 File Manifest\n")
    for f in FILES_TO_INCLUDE:
        lines.append(f"- `{f}`")
    lines.append("\n---\n")

    for f_name in FILES_TO_INCLUDE:
        f_path = os.path.join(ROOT_DIR, f_name)
        if os.path.exists(f_path):
            lang = "python" if f_name.endswith(".py") else ("json" if f_name.endswith(".json") else "markdown")
            lines.append(f"\n## 📄 File: `{f_name}`\n")
            lines.append(f"```{lang}")
            with open(f_path, "r", encoding="utf-8", errors="ignore") as src:
                lines.append(src.read())
            lines.append("```\n")
            lines.append("---\n")

    with open(OUTPUT_DIGEST_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

    print(f"Generated {OUTPUT_DIGEST_FILE} ({os.path.getsize(OUTPUT_DIGEST_FILE):,} bytes)")


if __name__ == "__main__":
    generate_digest()
