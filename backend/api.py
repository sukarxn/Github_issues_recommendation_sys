from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
from core import recommend_issues, cache, clear_profile_embeddings_cache, clear_reference_embeddings_cache
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder


app = FastAPI(title="GitHub Issues Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    language: Optional[str] = "all"
    per_page: Optional[int] = 20
    top_n: Optional[int] = 100
    student_profile: Optional[str] = None
    model: Optional[str] = "all-MiniLM-L6-v2"

@app.post("/recommend")
def recommend(req: RecommendRequest):
    issues = recommend_issues(
        per_page=req.per_page,
        top_n=req.top_n,
        student_profile=req.student_profile,
    )
    return {"recommendations": jsonable_encoder(issues)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.delete("/cache/clear")
def clear_cache():
    """Clear all cached data (issues and profile embeddings)."""
    try:
        cache.clear()
        return {"status": "All cache cleared successfully"}
    except Exception as e:
        return {"status": "Failed to clear cache", "error": str(e)}

@app.delete("/cache/clear-profiles")
def clear_profile_cache():
    """Clear only cached profile embeddings."""
    try:
        clear_profile_embeddings_cache()
        return {"status": "Profile embeddings cache cleared successfully"}
    except Exception as e:
        return {"status": "Failed to clear profile cache", "error": str(e)}

@app.delete("/cache/clear-references")
def clear_reference_cache():
    """Clear only cached reference embeddings."""
    try:
        clear_reference_embeddings_cache()
        return {"status": "Reference embeddings cache cleared successfully"}
    except Exception as e:
        return {"status": "Failed to clear reference cache", "error": str(e)}

@app.get("/cache/stats")
def cache_stats():
    """Get detailed cache statistics."""
    try:
        total_items = len(cache)
        profile_items = len([k for k in cache.keys() if isinstance(k, str) and k.startswith("profile_embedding_")])
        issue_items = len([k for k in cache.keys() if isinstance(k, str) and k.startswith("issues_")])
        
        return {
            "total_cache_size": total_items,
            "profile_embeddings_cached": profile_items,
            "issue_caches": issue_items,
            "cache_location": "/tmp/github_issues_cache"
        }
    except Exception as e:
        return {"error": str(e)}