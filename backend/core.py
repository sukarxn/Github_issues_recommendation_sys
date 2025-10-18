import requests
from typing import List, Dict, Tuple, Optional
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

def _auth_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-issues-reco/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def fetch_top_repositories(language: Optional[str], top_n: int = 100) -> List[Tuple[str, str, int]]:
    url = "https://api.github.com/search/repositories"
    headers = _auth_headers()
    q = "stars:>0"
    if language:
        q += f" language:{language}"
    params = {
        "q": q,
        "per_page": max(1, min(int(top_n), 100)),
        "sort": "stars",
        "order": "desc",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    repos: List[Tuple[str, str, int]] = []
    for it in items:
        full = it.get("full_name", "")
        if "/" not in full:
            continue
        owner, repo = full.split("/", 1)
        repos.append((owner, repo, int(it.get("stargazers_count", 0))))
    return repos

def fetch_repo_good_first_issues(owner: str, repo: str, limit: int) -> List[Dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = _auth_headers()
    params = {
        "state": "open",
        "sort": "updated",
        "direction": "desc",
        "per_page": max(1, min(int(limit), 100)),
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    issues = []
    wanted = {"good first issue", "good-first-issue"}
    for item in r.json():
        if "pull_request" in item:
            continue
        labels = {str(l.get("name", "")).strip().casefold() for l in item.get("labels", [])}
        if labels & wanted:
            issues.append({
                "title": item.get("title", ""),
                "body": item.get("body", ""),
                "url": item.get("html_url", ""),
                "repo": f"{owner}/{repo}",
            })
            if len(issues) >= limit:
                break
    return issues

def fetch_github_issues(language: str = "all", per_page: int = 20, top_n: int = 100) -> List[Dict]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        orig = top_n
        top_n = min(top_n, 30)
    repos = fetch_top_repositories(language or None, top_n=min(100, top_n))
    remaining = max(1, int(per_page))
    all_issues: List[Dict] = []
    for owner, repo, _stars in repos:
        batch = fetch_repo_good_first_issues(owner, repo, limit=min(remaining, 100))
        if batch:
            all_issues.extend(batch)
            remaining = per_page - len(all_issues)
            if remaining <= 0:
                break
    return all_issues[:per_page]

def create_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    return SentenceTransformer(model_name)

def generate_issue_embeddings(issues: List[Dict], model: SentenceTransformer) -> np.ndarray:
    if not issues:
        return np.array([])
    texts = [
        f"{issue.get('title', '').strip()} {issue.get('body', '').strip()}"
        for issue in issues
    ]
    return model.encode(texts, show_progress_bar=False)

def generate_student_profile_embedding(profile_text: str, model: SentenceTransformer) -> np.ndarray:
    return model.encode(profile_text, show_progress_bar=False)

def compute_similarities(student_embedding: np.ndarray, issue_embeddings: np.ndarray) -> np.ndarray:
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([student_embedding], issue_embeddings)[0]

def rank_issues_by_similarity(
    issues: List[Dict], 
    student_embedding: np.ndarray, 
    issue_embeddings: np.ndarray
) -> List[Tuple[Dict, float]]:
    similarities = compute_similarities(student_embedding, issue_embeddings)
    ranked = list(zip(issues, similarities))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def recommend_issues(
    language: str = "all",
    per_page: int = 20,
    top_n: int = 100,
    student_profile: Optional[str] = None,
    model_name: str = 'all-MiniLM-L6-v2',
) -> List[Dict]:
    issues = fetch_github_issues(language, per_page, top_n)
    if student_profile:
        model = create_embedding_model(model_name)
        issue_embeddings = generate_issue_embeddings(issues, model)
        student_embedding = generate_student_profile_embedding(student_profile, model)
        ranked_issues = rank_issues_by_similarity(issues, student_embedding, issue_embeddings)
        return [
            {
                **issue,
                "similarity": float(f"{score:.4f}")
            }
            for issue, score in ranked_issues
        ]
    else:
        return issues
