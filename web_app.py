"""
FastAPI Interactive Web Application for LeetCode Intelligence, Auto-Classification,
Cross-Platform Alternatives, Continuous Scraping & Two-Way Reverse MCP Copilot
"""

import os
import json
import time
import asyncio
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import pandas as pd

from ml_models import LeetCodeIntelligenceEngine
from scraper_engine import ContinuousIngestionWorker, CrossPlatformMapper, LeetCodeScraper

app = FastAPI(title="LeetCode AI Intelligence & Continuous Ingestion Hub")

# Initialize Engine & Background Ingestion Worker
engine = LeetCodeIntelligenceEngine()
engine.load_models()

crawler_worker = ContinuousIngestionWorker(engine, poll_interval_seconds=45)

# Precompute lists for UI dropdowns
ALL_COMPANIES = sorted(list(engine.company_classifier.target_companies))
ALL_DIFFICULTIES = ["Easy", "Medium", "Hard"]

all_tags = set()
for tags in engine.df["topic_tags"]:
    if isinstance(tags, (list, pd.Series)):
        all_tags.update(tags)
    elif isinstance(tags, str) and tags.strip():
        all_tags.update([t.strip() for t in tags.split(";")])
ALL_TOPICS = sorted(list(all_tags))

# In-Memory Event Queue for Real-Time Reverse MCP SSE Broadcasts
AGENT_EVENTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "title": "Agent Copilot Connected",
        "action_type": "status",
        "content": "LeetCode DSA Intelligence MCP Server & Web Bridge initialized and listening.",
        "problem_slug": ""
    }
]
EVENT_SUBSCRIBERS = set()
import queue_manager
from vector_store import LeetCodeVectorStore

# Initialize persistent vector store
vector_store = LeetCodeVectorStore()


def log_user_query_to_file(query_type: str, query_text: str, problem_slug: str = "", code: str = "", rating: str = "moderate") -> Dict[str, Any]:
    """Appends user queries to the persistent queue."""
    entry = {
        "id": int(time.time() * 1000),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": query_type,
        "query_text": query_text,
        "problem_slug": problem_slug,
        "code": code,
        "rating": rating,
        "status": "pending"
    }
    queue_manager.enqueue_task(entry)
    return entry


class PredictRequest(BaseModel):
    title: Optional[str] = ""
    description: str
    difficulty: Optional[str] = "Medium"
    topic_tags: Optional[List[str]] = None
    top_k: Optional[int] = 8


class PatternPredictRequest(BaseModel):
    title: Optional[str] = ""
    description: str
    top_k: Optional[int] = 5


ALL_DIFFICULTY_TIERS = ["Easy", "Easy-Medium", "Medium", "Medium-Hard", "Hard"]


class FilterRequest(BaseModel):
    company: Optional[str] = None
    difficulty: Optional[str] = None
    difficulty_tier: Optional[str] = None
    topic: Optional[str] = None
    cluster_id: Optional[int] = None
    timeframe: Optional[str] = None
    search_query: Optional[str] = None
    max_direct: Optional[int] = 30
    max_similar: Optional[int] = 20


class ScrapeRequest(BaseModel):
    slug_or_url: str


class CrawlerToggleRequest(BaseModel):
    enable: bool


class BroadcastPayload(BaseModel):
    title: str
    action_type: str  # 'code_review', 'adaptive_step', 'study_plan', 'alert', 'status'
    content: str
    problem_slug: Optional[str] = ""


class SolutionAnalysisRequest(BaseModel):
    problem_slug: str
    candidate_code: str
    language: Optional[str] = "python"
    performance_rating: Optional[str] = "moderate"  # 'struggled', 'moderate', 'mastered'


@app.get("/api/metadata")
def get_metadata():
    """Returns dropdown metadata and real-time database stats."""
    return {
        "companies": ALL_COMPANIES,
        "difficulties": ALL_DIFFICULTIES,
        "difficulty_tiers": ALL_DIFFICULTY_TIERS,
        "topics": ALL_TOPICS,
        "total_problems": len(engine.df),
        "clusters_count": len(engine.cluster_engine.cluster_summaries),
        "clusters": list(engine.cluster_engine.cluster_summaries.values()),
        "crawler_running": crawler_worker.is_running,
        "total_crawled": crawler_worker.total_ingested_count
    }


@app.get("/api/archetypes")
def get_all_archetypes():
    """Returns the 15 Unified Algorithmic Archetypes with 5-tier distributions and GFG Roadmap."""
    return JSONResponse(content={
        "status": "success",
        "paradigms": engine.cluster_engine.core_paradigms,
        "phases": engine.cluster_engine.roadmap_phases,
        "archetypes": list(engine.cluster_engine.cluster_summaries.values())
    })


@app.get("/api/cluster/{cluster_id}")
def get_cluster_details(cluster_id: int):
    """Returns granular 5-tier problem breakdown and archetype analysis for a cluster."""
    summary = engine.cluster_engine.cluster_summaries.get(cluster_id)
    if not summary:
        return JSONResponse(content={"status": "not_found", "message": f"Cluster #{cluster_id} not found."}, status_code=404)
    return JSONResponse(content={"status": "success", "data": summary})


@app.get("/api/cluster/{cluster_id}/tier/{tier_name}")
def get_cluster_tier_problems(cluster_id: int, tier_name: str):
    """Returns problems for a specific difficulty tier within an archetype."""
    summary = engine.cluster_engine.cluster_summaries.get(cluster_id)
    if not summary:
        return JSONResponse(content={"status": "not_found", "message": f"Cluster #{cluster_id} not found."}, status_code=404)
    
    # Normalize tier name (e.g. easy-medium, medium-hard)
    tier_key = None
    for k in ["Easy", "Easy-Medium", "Medium", "Medium-Hard", "Hard"]:
        if k.lower() == tier_name.lower().replace("_", "-"):
            tier_key = k
            break
    
    if not tier_key:
        return JSONResponse(content={"status": "invalid_tier", "message": f"Tier '{tier_name}' is invalid. Use Easy, Easy-Medium, Medium, Medium-Hard, or Hard."}, status_code=400)
    
    problems = summary.get("problems_by_tier", {}).get(tier_key, [])
    return JSONResponse(content={
        "status": "success",
        "cluster_id": cluster_id,
        "archetype": summary.get("title"),
        "tier": tier_key,
        "problem_count": len(problems),
        "problems": problems
    })


@app.post("/api/predict")
def predict_company(req: PredictRequest):
    """Predicts which companies can/will ask a given problem, plus 5 platform alternatives."""
    try:
        results = engine.predict_problem_companies(
            problem_description=req.description,
            title=req.title or "",
            difficulty=req.difficulty or "Medium",
            topic_tags=req.topic_tags or [],
            top_k=req.top_k or 8
        )
        return JSONResponse(content={"status": "success", "data": results})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/predict/pattern")
def predict_patterns(req: PatternPredictRequest):
    """Predicts multi-label algorithmic patterns from problem description using NLP BCE classifier."""
    try:
        results = engine.predict_patterns(
            text=req.description,
            title=req.title or "",
            top_k=req.top_k or 5
        )
        return JSONResponse(content={"status": "success", "data": results})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/filter-recommend")
@app.post("/api/problems/filter")
def filter_and_recommend(req: FilterRequest):
    """Filters problems and finds high-probability similar unasked questions."""
    try:
        results = engine.filter_and_recommend(
            company=req.company,
            difficulty=req.difficulty,
            difficulty_tier=req.difficulty_tier,
            topic=req.topic,
            cluster_id=req.cluster_id,
            timeframe=req.timeframe,
            search_query=req.search_query,
            max_direct=req.max_direct or 30,
            max_similar=req.max_similar or 20
        )
        return JSONResponse(content={"status": "success", "data": results})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.get("/api/problem/{identifier}")
def get_problem_details(identifier: str):
    """Fetches complete problem details, 5 cross-platform alternatives, and 5 similar counterparts."""
    problem = engine.get_problem_by_id_or_slug(identifier)
    if not problem:
        return JSONResponse(content={"status": "not_found", "message": f"Problem '{identifier}' not found."}, status_code=404)
    return JSONResponse(content={"status": "success", "data": problem})


@app.post("/api/scrape-and-ingest")
@app.post("/api/scrape")
def scrape_and_ingest(req: ScrapeRequest):
    """Scrapes a single problem by slug/URL, auto-classifies it, and appends to live DB."""
    try:
        raw_input = req.slug_or_url.strip()
        slug = raw_input.rstrip("/").split("/")[-1]
        result = crawler_worker.ingest_single_slug(slug)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.post("/api/crawler/toggle")
def toggle_crawler(req: CrawlerToggleRequest):
    """Starts or stops the background continuous crawler worker."""
    if req.enable:
        crawler_worker.start()
    else:
        crawler_worker.stop()
    return JSONResponse(content={"status": "success", "crawler_running": crawler_worker.is_running})


@app.get("/api/crawler/status")
def get_crawler_status():
    """Returns real-time status and recent ingestion activity log."""
    return JSONResponse(content={"status": "success", "data": crawler_worker.get_status()})


@app.get("/api/clusters")
def get_clusters():
    """Returns all 30 algorithmic archetype clusters."""
    return JSONResponse(content={"status": "success", "data": list(engine.cluster_engine.cluster_summaries.values())})


# ==============================================================================
# Two-Way Reverse MCP & Real-Time Agent Communication Bridge
# ==============================================================================

@app.post("/api/agent/broadcast")
async def broadcast_agent_action(payload: BroadcastPayload):
    """
    Reverse MCP Endpoint: Receives actions from mcp_server.py or Antigravity agents
    and broadcasts them to active web browsers in real-time.
    """
    event = {
        "id": len(AGENT_EVENTS) + 1,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "title": payload.title,
        "action_type": payload.action_type,
        "content": payload.content,
        "problem_slug": payload.problem_slug or ""
    }
    AGENT_EVENTS.append(event)
    if len(AGENT_EVENTS) > 50:
        AGENT_EVENTS.pop(0)

    # Notify connected SSE queues
    for queue in list(EVENT_SUBSCRIBERS):
        try:
            await queue.put(event)
        except Exception:
            EVENT_SUBSCRIBERS.discard(queue)

    return JSONResponse(content={"status": "broadcasted", "event": event})


@app.get("/api/agent/events")
def get_agent_events():
    """Returns recent agent broadcast events."""
    return JSONResponse(content={"status": "success", "events": AGENT_EVENTS})


@app.get("/api/agent/stream")
async def agent_event_stream(request: Request):
    """Server-Sent Events (SSE) stream for real-time agent updates in the browser."""
    queue = asyncio.Queue()
    EVENT_SUBSCRIBERS.add(queue)

    async def event_generator():
        try:
            # Yield recent events on initial connection
            for ev in AGENT_EVENTS[-5:]:
                yield f"data: {json.dumps(ev)}\n\n"
            
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive ping
                    yield ": ping\n\n"
        finally:
            EVENT_SUBSCRIBERS.discard(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class UserQueryRequest(BaseModel):
    query_text: Optional[str] = ""
    query_type: Optional[str] = "general"
    problem_slug: Optional[str] = ""
    code: Optional[str] = ""
    rating: Optional[str] = "moderate"


@app.post("/api/agent/submit-query")
def submit_query_endpoint(req: UserQueryRequest):
    """Saves user query to transactional SQLite queue for 5-second agent processing."""
    task_id = queue_manager.enqueue_task(
        query_type=req.query_type or "general",
        query_text=req.query_text or "",
        problem_slug=req.problem_slug or "",
        code=req.code or "",
        rating=req.rating or "moderate"
    )
    return JSONResponse(content={
        "status": "queued",
        "message": f"Query #{task_id} saved to transactional SQLite database. Agent scheduled to process in 5s.",
        "task_id": task_id
    })


@app.get("/api/agent/queue")
def get_queued_queries():
    """Returns recent queries from the transactional SQLite queue."""
    queries = queue_manager.list_recent_queries(limit=50)
    return JSONResponse(content={"status": "success", "queries": queries})


@app.post("/api/agent/analyze-solution")
def analyze_solution_endpoint(req: SolutionAnalysisRequest):
    """
    Web-to-Agent Trigger: Evaluates candidate solution and logs query to persistent file.
    """
    # Log query to SQLite queue
    queue_manager.enqueue_task(
        query_type="code_review",
        query_text=f"Code submission for {req.problem_slug}",
        problem_slug=req.problem_slug,
        code=req.candidate_code,
        rating=req.performance_rating or "moderate"
    )

    p = engine.get_problem_by_id_or_slug(req.problem_slug)
    if not p:
        return JSONResponse(content={"status": "error", "message": f"Problem '{req.problem_slug}' not found."}, status_code=404)

    diff = p.get("difficulty", "Medium")
    cluster = p.get("cluster_title", "General")
    code = req.candidate_code

    # Static heuristic analysis
    code_lower = code.lower()
    patterns = []
    if "for " in code_lower or "while " in code_lower: patterns.append("Iterative Loops")
    if "def " in code and any(f in code for f in ["return self.", "solve(", "dfs(", "helper("]): patterns.append("Recursion / DFS")
    if "memo" in code_lower or "dp" in code_lower or "@lru_cache" in code_lower: patterns.append("Dynamic Programming / Memoization")
    if "dict(" in code_lower or "{}" in code_lower or "counter" in code_lower: patterns.append("Hash Map / Counting")
    if "heapq" in code_lower or "heappush" in code_lower: patterns.append("Priority Queue / Heap")

    # Adaptive recommendation step
    direction = "decrease" if req.performance_rating == "struggled" else ("increase" if req.performance_rating == "mastered" else "similar")
    
    if direction == "decrease":
        target_diff = "Easy" if diff in ["Medium", "Hard"] else "Easy"
        intent = f"Foundational practice for {cluster}"
    elif direction == "increase":
        target_diff = "Hard" if diff in ["Medium", "Hard"] else "Medium"
        intent = f"Advanced follow-up challenge for {cluster}"
    else:
        target_diff = diff
        intent = f"Reinforcement challenge at same difficulty ({diff})"

    # Find candidate next problems
    step_probs = engine.df[
        (engine.df["cluster_title"] == cluster) &
        (engine.df["difficulty"] == target_diff) &
        (engine.df["task_id"] != req.problem_slug)
    ]
    
    recommended_steps = []
    if len(step_probs) > 0:
        for _, row in step_probs.head(3).iterrows():
            t_id = str(row["task_id"])
            recommended_steps.append({
                "task_id": t_id,
                "difficulty": row["difficulty"],
                "cluster_title": cluster,
                "platform_alternatives": CrossPlatformMapper.get_5_alternatives(t_id)
            })
    else:
        for sim in p.get("similar_counterparts", [])[:3]:
            recommended_steps.append({
                "task_id": sim["task_id"],
                "difficulty": sim["difficulty"],
                "cluster_title": sim.get("cluster_title", cluster),
                "platform_alternatives": CrossPlatformMapper.get_5_alternatives(sim["task_id"])
            })

    result = {
        "problem_title": req.problem_slug,
        "difficulty": diff,
        "cluster_archetype": cluster,
        "detected_patterns": patterns,
        "performance_rating": req.performance_rating,
        "stepping_intent": intent,
        "recommended_next_problems": recommended_steps,
        "target_companies": p.get("top_companies", [])[:5]
    }
    return JSONResponse(content={"status": "success", "data": result})


from fastapi.staticfiles import StaticFiles

# Mount React static assets if built
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/", response_class=HTMLResponse)
def index():
    # Prefer compiled modern React UI
    react_index = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(react_index):
        with open(react_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    # Fallback to templates/index.html
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Frontend UI not found</h1>")


# Background Queue Worker Thread Loop (Runs every 5 seconds)
def _start_queue_worker_background():
    import agent_queue_worker
    worker_thread = threading.Thread(target=agent_queue_worker.run_agent_loop, kwargs={"interval_seconds": 5}, daemon=True)
    worker_thread.start()

_start_queue_worker_background()


if __name__ == "__main__":
    import uvicorn
    print("Starting LeetCode Intelligence Dashboard at http://localhost:8000 ...")
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=False)
