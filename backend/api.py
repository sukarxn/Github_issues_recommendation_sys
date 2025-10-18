from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
from core import recommend_issues
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
        language=req.language,
        per_page=req.per_page,
        top_n=req.top_n,
        student_profile=req.student_profile,
        model_name=req.model,
    )
    return {"recommendations": jsonable_encoder(issues)}

@app.get("/health")
def health():
    return {"status": "ok"}
